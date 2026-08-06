# File Upload Service — MVP Spec

**Status:** MVP · **Scope:** Backend only, `curl` clients, no UI.

This spec is the source of truth. Code and tests are checked against it. Keywords MUST / SHOULD / MAY per RFC 2119.

---

## 1. Overview

A backend HTTP service that lets authenticated users upload, list, download, and delete files. Files are private to their owner. Bytes live in object storage (S3); the service stores only metadata.

**In scope (MVP):** upload, download, list, delete; per-user daily quota; 100 MB size cap.

**Out of scope (MVP):** UI, multipart/resumable upload, CDN, virus scanning, sharing between users, rate limiting.

**Success criteria:**
- A 100 MB file uploads and downloads successfully via `curl`.
- A user is blocked at the 11th upload within 24 hours.
- No file is accessible to any user other than its owner.

---

## 2. Requirements

### Functional
- **F1** — A user MUST be able to upload a file up to **100 MB**.
- **F2** — A user MUST NOT have more than **10 files counted against them in any rolling 24-hour window** (see §6 for what "counted" means).
- **F3** — A user MUST be able to download their own file.
- **F4** — A user MUST be able to list their own files.
- **F5** — A user MUST be able to delete their own file.
- **F6** — A user MUST NOT be able to read, list, or delete another user's files.
- **F7** — An upload larger than 100 MB MUST be rejected.

### Non-functional
- **N1** — Bytes MUST NOT flow through the application tier (app stays out of the data path).
- **N2** — The application tier MUST be stateless (no file data on local disk).
- **N3** — Every request MUST be authenticated.

---

## 3. Domain Model

### `files`
| Field | Type | Notes |
|---|---|---|
| `file_id` | string (PK) | Stable public identifier, e.g. `f_abc123` |
| `user_id` | string | Owner |
| `filename` | string | Client-supplied display name |
| `storage_key` | string (unique) | Where bytes live in S3, e.g. `u_42/f_abc123` |
| `size` | int | Bytes |
| `status` | enum | `pending` \| `complete` |
| `created_at` | timestamp (UTC) | Used for quota window |

### Invariants
- **I1** — `storage_key` is unique.
- **I2** — A presigned URL is **never** persisted (it is a transient credential, regenerated on demand from `storage_key`).
- **I3** — Status transitions only: `pending → complete`, or `pending → (deleted by GC)`. No other transitions.
- **I4** — A `pending` file is NOT downloadable and does NOT appear in list results.

---

## 4. API Contract

All requests require `Authorization: Bearer <token>`. All responses are JSON unless noted.

### `POST /files` — request an upload
Creates a `pending` record and returns a presigned URL for direct upload to S3.

Request:
```json
{ "filename": "report.zip", "size": 104857600 }
```
Responses:
- `201` `{ "file_id": "f_abc123", "upload_url": "https://s3...?X-Amz-Signature=..." }`
- `400` invalid body / size > 100 MB
- `429` quota exceeded (10/day)

### `PUT <upload_url>` — upload bytes (to S3 directly, not this service)
- Client PUTs raw bytes. S3 enforces the 100 MB cap via the signed condition.

### `POST /files/{file_id}/complete` — finalize
Marks the upload `complete` after bytes are in S3.
- `200` `{ "file_id": "f_abc123", "status": "complete" }`
- `404` not found / not owned

### `GET /files/{file_id}/download` — get a download URL
- `200` `{ "download_url": "https://s3...?X-Amz-Signature=..." }`
- `404` not found / not owned / still `pending`

### `GET /files` — list own files
- `200` `{ "files": [ { "file_id", "filename", "size", "created_at" } ] }` (only `complete`)

### `DELETE /files/{file_id}`
- `204` deleted (removes S3 object + metadata row)
- `404` not found / not owned

---

## 5. Key Flow — upload

```
1. curl ─► POST /files            app: auth → quota check → insert row(status=pending)
                                       → return presigned PUT URL (size condition = 100MB)
2. curl ─► PUT upload_url (100MB) ─► S3     (app not involved)
3. curl ─► POST /files/{id}/complete   app: verify owner → status = complete
```

If step 3 never happens (client abandons), a GC sweep removes the `pending` row and any S3 object (see §6).

---

## 6. Cross-cutting Rules

### AuthZ
- Every `/files/{id}` operation MUST verify `file.user_id == caller`. A `file_id` alone grants nothing.

### Quota (F2) — resolved decisions
- **Window:** rolling 24 hours, measured in **UTC**.
- **Counted statuses:** both `pending` and `complete` count (prevents bypass by firing many concurrent uploads).
- **Query:** `count(*) WHERE user_id = ? AND created_at >= now() - 24h AND status IN ('pending','complete')`.
- **Concurrency:** the count-and-insert MUST be atomic (transaction with `SELECT ... FOR UPDATE` on the user row) so concurrent requests cannot both pass at count = 9.

### Size cap (F7)
- Enforced by S3 via the presigned URL's `content-length-range` condition. The app also rejects `size > 100 MB` in the `POST /files` body as an early check.

### Garbage collection
- A periodic job deletes `pending` rows (and their S3 objects) older than **30 minutes**. This also frees quota slots consumed by abandoned uploads.

---

## 7. Failure & Edge Behavior

| Case | Behavior |
|---|---|
| Upload > 100 MB | S3 rejects the PUT; app early-rejects in `POST /files` → `400` |
| Abandoned upload (no complete) | Row stays `pending`, invisible in list/download; GC removes it after 30 min |
| Duplicate `POST /files/{id}/complete` | Idempotent — already `complete` returns `200` |
| Access to another user's file | `404` (not `403`, to avoid leaking existence) |
| Download of a `pending` file | `404` |
| Expired presigned URL | Client re-requests via `POST /files` (upload) or `GET .../download` |

---

## 8. Deferred (post-MVP)

- **Multipart / resumable upload** — MVP uses a single presigned PUT; a failed 100 MB upload is retried whole. Add multipart when retry cost or throughput becomes a problem.
- **CDN** on downloads — add if the same files are read repeatedly.
- **Virus scanning** — required only if files are ever served to other users.
- **Rate limiting** — add at the edge if the service is public.
- **S3 event-based completion** — MVP uses the client `complete` callback with GC as backstop; switch to S3 events for robustness later.

---

## 9. Acceptance Tests

| # | Requirement | Test |
|---|---|---|
| T1 | F1 | Upload a 100 MB file end-to-end (POST → PUT → complete); it appears in list |
| T2 | F7 | POST with `size = 100 MB + 1` → `400`; oversized PUT → S3 rejects |
| T3 | F2 | 10 uploads succeed; 11th within 24h → `429` |
| T4 | F2 (race) | 11 concurrent `POST /files` → at most 10 succeed |
| T5 | F6 | User B `GET/DELETE` on User A's file → `404` |
| T6 | I4 | Download/list of a `pending` file → not returned |
| T7 | GC | A `pending` row older than 30 min is removed and its quota slot freed |
