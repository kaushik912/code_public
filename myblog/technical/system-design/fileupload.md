# File Upload Service — Design

**Scope:** Backend only. Clients use `curl`. Focused on the **100 MB / file** case.

## Requirements

| Constraint | Value |
|---|---|
| Users | Thousands (~10k) |
| Max file size | **100 MB per file** |
| Upload limit | **10 files per user per day** |
| Interface | HTTP API driven by `curl` (no UI) |

### Capacity math (why the design is shaped this way)

```
10,000 users × 10 files × 100 MB  =  up to ~10 TB/day ingest (worst case)
```

Two facts drive every decision below:

1. **Bytes cannot flow through the app tier** — proxying ~TB/day of 100 MB bodies would force us to scale app servers just to move bytes.
2. **A single 100 MB upload is fragile and long-lived** — tens of seconds over a home connection, and it can drop halfway. Uploads must survive interruption.

---

## Architecture

```
                  ┌──────────────┐
   curl ─────────►│ Load Balancer│
                  └──────┬───────┘
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        ┌────────┐  ┌────────┐  ┌────────┐   Stateless app tier:
        │  App   │  │  App   │  │  App   │     - authenticate / authorize
        └───┬────┘  └────────┘  └────────┘     - enforce quota (atomic)
            │                          │        - sign URLs, record metadata
   presign  │                   metadata│        NOT in the byte path.
   & events │                          ▼
            │                    ┌──────────────┐
            │                    │   Postgres   │  files{ id, user, key,
            │                    └──────────────┘         size, status, created_at }
            ▼
      ┌──────────────┐     curl ──100MB──► (direct, via presigned URL / multipart)
      │  S3 bucket   │◄──────────────────────────────────────────────────────────
      │  the bytes   │
      └──────┬───────┘
             └── upload-finished event ──► App (flip pending → complete)
      + lifecycle rule: delete abandoned/expired objects
```

### Core principle: split blob from metadata

- **Bytes** → object storage (S3 / MinIO). Effectively infinite, durable, someone else's problem. Never local disk (that would make app servers stateful).
- **Facts about the bytes** → a database row.

Keeping bytes out of the app tier is what lets the app tier stay **stateless** — N interchangeable servers behind the load balancer, scaled by just booting more.

---

## Metadata model

The DB stores the **stable identity** of a file, never the transient signed URL.

```
files
├── file_id        f_abc123          stable identifier
├── user_id        u_42
├── storage_key    u_42/f_abc123     WHERE the bytes live in S3   ← store this
├── size           104857600
├── content_hash   sha256:...
├── status         pending | complete
├── upload_id      (S3 multipart handle, while in progress)
└── created_at     2026-08-06T...
```

**Do NOT persist the presigned URL.** It is a transient bearer credential, not data:

- **It expires** (~15 min) — a stored URL is a dead string minutes later.
- **It is derivable** — `signed_url = sign(storage_key, operation, expiry, secret)`. We already hold the key; recomputing is a sub-millisecond local crypto op, no S3 round-trip. Anything cheaply recomputable shouldn't be a second source of truth.
- **It is a secret** — whoever holds it can read/write those bytes. Don't persist bearer credentials.
- **One key → many URLs** — different operations/expiries/callers. "The" URL doesn't even make sense.

Mental model: `storage_key` is the password (durable, stored); the presigned URL is a session token (minted fresh per request, expires fast, never written down).

> `upload_id` (multipart) is the one URL-adjacent value we *do* persist — it is stable identity for an in-progress upload, not a credential.

---

## Upload flow — presigned URLs (app leaves the byte path)

```
1. curl ─► [App]  "I want to upload report.zip (100MB)"
                   │  app: authenticate → check quota → insert row (status=pending)
                   │       → generate presigned PUT URL (with 100MB size condition)
                   └─► returns { file_id, upload_url }

2. curl ──100MB──────────────────► [S3]     (app never touches a byte)

3. S3 ──event──► [App]  "f_abc123 finished"
                   │  app flips row status: pending → complete
```

A **presigned URL** = a time-limited, operation-scoped, signed URL: "whoever holds this may PUT to exactly this key for the next 15 minutes." The app authorizes and records; S3 moves the bytes. Upload bandwidth now scales with S3, not with app-server count.

### Two-phase state

The metadata row (`pending`) exists **before** the bytes do. A completion signal (S3 event notification, or a client callback `POST /files/{id}/complete`) flips it to `complete`. Until then the file exists but isn't usable.

- **Garbage collection:** a sweep job deletes `pending` rows (and their partial objects) older than N minutes — abandoned uploads. Also enforced via an S3 lifecycle rule.

### Enforcing the 100 MB cap

The app is no longer in the byte path, so the cap must **travel with the signature**: set S3's `content-length-range` condition inside the presigned URL. S3 itself rejects an oversized PUT. An app-side check is no longer sufficient.

---

## Resumable uploads — multipart

A 100 MB upload that fails at 95 MB must not restart from zero. Multipart splits the file into chunks (5–10 MB), uploaded independently; S3 stitches them on completion.

```
curl ─► [App]  "start multipart for f_abc123"   → upload_id + presigned URL per part
curl ──part1──► S3   ✓ returns ETag
curl ──part2──► S3   ✗ fails → retry ONLY part2
curl ──part3──► S3   ✓
curl ─► [App]  "complete: [{1,etag},{2,etag},{3,etag}]"  → S3 assembles
```

The unit of failure shrinks from the whole file to one chunk — retries get cheap, and parts can upload in parallel for throughput.

**Threshold:** use multipart only above ~20 MB; a single presigned PUT below it. (For hand-driven `curl`, the multipart loop needs a small script.)

---

## Quota — 10 files/user/day (the real correctness landmine)

### Count over a window, don't reset a counter

Avoid a cron-reset counter (race-prone, a failure point). Count over a time window:

```sql
SELECT count(*) FROM files
WHERE user_id = $1
  AND created_at >= now() - interval '24 hours'
  AND status IN ('pending', 'complete');
```

### Three decisions to pin down

1. **Rolling 24h vs. calendar-day** — and if calendar-day, **in which timezone?** These enforce differently.
2. **When to count** — count `pending` + `complete` toward the limit (so 100 simultaneous starts can't bypass it), but **expire abandoned `pending` rows quickly** so genuine failures free up slots.
3. **Do failed/abandoned uploads count?** Follows from (2) + GC timing.

### The race (must handle)

A user firing 10 uploads concurrently can each read `count = 9` and all pass — a check-then-act race → 19 files. Make count-and-insert **atomic**: one transaction with `SELECT ... FOR UPDATE` on the user row (or a DB counter/constraint) so concurrent requests serialize. Silent bug — only appears under concurrency, passes every single-threaded test.

---

## API (curl-driven)

```bash
# 1. Request an upload — returns file_id + presigned upload URL(s)
curl -X POST https://api.example.com/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"report.zip","size":104857600}'
# → 201 {"file_id":"f_abc123","upload_url":"https://bucket.s3...?X-Amz-Signature=..."}
```
```bash
# 2. Upload bytes directly to S3 (app not involved)
curl -X PUT "$UPLOAD_URL" --data-binary @report.zip
```
```bash
# 3. Mark complete (if not using S3 events)
curl -X POST https://api.example.com/files/f_abc123/complete \
  -H "Authorization: Bearer $TOKEN"
```
```bash
# Download — app returns a fresh presigned GET URL
curl https://api.example.com/files/f_abc123/download \
  -H "Authorization: Bearer $TOKEN"
# → {"download_url":"https://bucket.s3...?X-Amz-Signature=..."}
```
```bash
# List my files
curl https://api.example.com/files -H "Authorization: Bearer $TOKEN"
```
```bash
# Delete
curl -X DELETE https://api.example.com/files/f_abc123 \
  -H "Authorization: Bearer $TOKEN"
```

**Non-negotiables:**
- **AuthN/AuthZ** on every operation — a `file_id` alone must never grant access; check `file.user_id == caller`.
- **Size cap** enforced via the presigned URL's `content-length-range`.
- **Idempotency** — client sends an `Idempotency-Key` (or dedupe on `content_hash`) so a retried request doesn't create duplicates or waste quota.

---

## Scaling levers (each independent)

| Bottleneck | Lever |
|---|---|
| More concurrent requests (auth/routing/signing) | Add stateless app servers behind the LB — linear. |
| Upload/download **bandwidth** | Already solved — bytes go client↔S3 directly. App tier is not in the path. |
| Storage capacity / durability | S3 scales for us (never local disk). |
| Metadata reads (list/lookup hot) | DB read replicas + cache hot lookups. Rows are tiny; bites last. |

---

## Deliberately deferred

- **CDN on downloads** — only if the same files are read repeatedly by many users. Often skip for private per-user files.
- **Virus scan / content validation** — required only if uploads are served to *other* users; run async via a queue after upload completes.
- **Rate limiting** — cheap at LB/app tier; add early if public.
