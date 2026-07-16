# System Design: One-Click Checkout

Here's a complete, interview-ready breakdown. I'll give you the solution first, then drill into the three hard parts (idempotency, inventory concurrency, and the usual gotchas), and finish with a **reusable template** you can apply to any "transactional flow" system design question.

---

## 1. Problem framing (say this out loud in the interview)

**One-click checkout** = user has a pre-saved payment method + shipping address, and a single tap must reliably: reserve inventory → charge payment → create an order → trigger fulfillment. The whole thing must be **correct under retries, concurrency, and partial failure**.

**Functional requirements**
- Place an order with one action (no cart/address/payment re-entry).
- Reserve stock so two people can't buy the last unit.
- Charge exactly once, even if the client retries.
- Return fast; do slow work (fulfillment, email) async.

**Non-functional requirements**
- **Correctness > latency**: never double-charge, never oversell.
- Low latency on the synchronous path (~hundreds of ms).
- High availability; graceful degradation.
- Scale: peak = flash sales (huge contention on few hot SKUs).

**Scope check to state:** "I'll assume payment is a saved token (PSP like Stripe/Adyen), and focus on the orchestration, idempotency, and inventory — not the payment cryptography or address service."

---

## 2. High-level architecture

```
Client ──(1) POST /checkout {Idempotency-Key}──► API Gateway
                                                     │
                                                     ▼
                                            Checkout / Order Service  ◄── Idempotency store (Redis/DB)
                                              │        │        │
                                     reserve  │        │ charge │  create order
                                              ▼        ▼        ▼
                                        Inventory   Payment    Order DB
                                         Service    Service   (source of truth)
                                              │
                                              └── emits events ──► Kafka ──► Fulfillment, Email, Analytics
```

**Two-phase mental model:**
- **Synchronous path** (must be fast + correct): validate → reserve inventory → authorize payment → persist order → return.
- **Asynchronous path** (eventual): capture payment, allocate warehouse, ship, notify — driven off an event log.

---

## 3. Idempotency (the #1 thing they're probing)

**The problem:** the client taps once but the network is unreliable — the request may be retried by the client, a load balancer, or a mobile app that lost the response. Without protection you charge twice and create two orders.

### Client-supplied idempotency key
- Client generates a **unique key per checkout attempt** (UUID) and sends it as a header: `Idempotency-Key: <uuid>`.
- The **same key is reused on retries** of that same logical operation; a new key = a genuinely new order.

### Server-side algorithm
```
On POST /checkout with key K:
  1. INSERT (K, status=IN_PROGRESS, request_hash) 
     using a UNIQUE constraint on K.
  2. If insert succeeds  → we own it; do the work; store the response; mark COMPLETED.
  3. If insert conflicts  → key already seen:
        - status COMPLETED  → return the stored response (do NOT re-execute).
        - status IN_PROGRESS → return 409 / "retry later" (or block briefly).
  4. Verify request_hash matches → if the same key is reused with a *different* 
     body, reject with 422 (prevents key reuse bugs).
```

Key points to mention:
- The **unique constraint is the concurrency primitive** — two simultaneous requests race on the INSERT; exactly one wins.
- Store the **final response** so retries are truly identical.
- Set a **TTL** on keys (e.g. 24h) — they're not permanent.
- **Idempotency must extend downstream:** pass the key (or a derived one) to the Payment PSP — every serious PSP accepts an idempotency key so the *charge* itself is deduped, not just your API.

### The subtle part: idempotency ≠ exactly-once across services
You can't get true distributed exactly-once. You get **at-least-once delivery + idempotent handlers = effectively-once**. Every consumer (fulfillment, email) must dedupe on `order_id`/`event_id`.

---

## 4. Inventory handling under concurrent contention

This is the other half they want. The scenario: **1000 people tap "buy" on the last 10 units simultaneously.** How do you not oversell?

### Option A — Pessimistic DB locking (`SELECT ... FOR UPDATE`)
```sql
BEGIN;
SELECT available FROM inventory WHERE sku = ? FOR UPDATE;   -- row lock
-- check available >= qty
UPDATE inventory SET available = available - qty WHERE sku = ?;
COMMIT;
```
- **Correct**, simple. But the row lock **serializes all buyers of a hot SKU** → throughput collapses under flash-sale contention. Good default answer, then critique it.

### Option B — Optimistic concurrency (version / conditional update)
```sql
UPDATE inventory
SET available = available - qty, version = version + 1
WHERE sku = ? AND available >= qty;      -- atomic guard, no explicit lock
-- affected rows == 0  → someone else took it; fail fast / retry
```
- No held locks; the `WHERE available >= qty` makes oversell **impossible** (the DB won't apply it). Retries on conflict. Scales far better; ideal when conflicts are common but the operation is cheap.
- This single conditional `UPDATE` is the cleanest thing to write on the whiteboard.

### Option C — Reserve-then-confirm (reservation pattern) ← **the real answer for checkout**
Decrementing on payment success is wrong (payment takes seconds; others buy meanwhile). Instead:

1. **Reserve** inventory *before* payment: create a reservation that holds `qty` for a **TTL** (e.g. 10 min).
   ```
   available = on_hand - reserved
   reserve:  UPDATE ... SET reserved = reserved + qty WHERE (on_hand - reserved) >= qty
   ```
2. **Authorize + capture payment.**
3. On success → **commit**: `on_hand -= qty; reserved -= qty` and create the order.
4. On failure/timeout → **release**: `reserved -= qty` (a background sweeper expires stale reservations).

This gives the user a held cart, avoids overselling, and doesn't block others beyond the reserved count.

### Option D — In-memory counter for extreme scale (flash sales)
For a Black-Friday hot SKU, even the DB is a bottleneck. Front the counter with **Redis** using an atomic `DECR` (or a Lua script for check-and-decrement):
```
-- Lua: atomic, single-threaded in Redis
if redis.call('GET', sku) >= qty then
   return redis.call('DECRBY', sku, qty)
else
   return -1   -- sold out
end
```
- Redis absorbs the thundering herd; DB is updated asynchronously as the durable record. Trade-off: you now need to **reconcile Redis ↔ DB** and handle Redis failure. Mention this only for the scale variant.

**How to present it:** "Default to a **reservation pattern backed by an atomic conditional update** (C+B). For flash-sale hot keys, add a **Redis atomic counter** in front (D). Avoid pessimistic locks except for low-contention items."

| Approach | Oversell-safe | Contention behavior | Use when |
|---|---|---|---|
| `FOR UPDATE` lock | ✅ | Serializes → slow | Low contention |
| Optimistic conditional update | ✅ | Fails fast, retries | Moderate/high contention |
| Reservation + TTL | ✅ | Holds stock fairly | **Checkout default** |
| Redis atomic counter | ✅ (needs reconcile) | Best throughput | Flash sales / hot SKUs |

---

## 5. Orchestrating the multi-step transaction: the Saga pattern

Checkout spans Inventory, Payment, and Order — you **can't** wrap them in one ACID transaction (different services/DBs). Use a **Saga**: a sequence of local transactions, each with a **compensating action** if a later step fails.

```
reserve inventory ──► authorize payment ──► create order ──► capture payment
       │                     │                                     
       └─ compensate:        └─ compensate:                        
          release reservation   void authorization                 
```
- **Orchestration** (a Checkout orchestrator drives steps) is usually cleaner to explain than choreography for this flow.
- Pair with the **Transactional Outbox pattern**: write the order *and* the "OrderPlaced" event in the **same DB transaction** to an outbox table; a relay publishes it to Kafka. This guarantees you never persist an order without emitting its event (or vice versa) — solves dual-write inconsistency.

---

## 6. Other concepts interviewers love here

- **Payment auth vs capture:** *authorize* on the sync path (hold funds, fast), *capture* async when you ship. Lets you cancel cleanly by voiding the auth.
- **Consistency model:** Order DB and payment are **strongly consistent**; fulfillment/email/analytics are **eventually consistent** via events.
- **State machine for the order:** `CREATED → PAYMENT_AUTHORIZED → CONFIRMED → FULFILLED / CANCELLED / FAILED`. Every transition is idempotent and logged. Great whiteboard artifact.
- **Failure handling:** retries with exponential backoff + jitter; **dead-letter queues** for poison events; the reservation sweeper for orphaned holds.
- **Rate limiting / abuse:** one-click makes accidental & fraudulent bursts easy — throttle per user, add fraud checks async.
- **Observability:** trace the idempotency key end-to-end; alert on oversell count, auth-failure rate, reservation-expiry rate.
- **CAP framing:** for inventory you favor **consistency** (don't oversell) over availability — better to say "sold out" than to oversell.

---

## 7. Reusable template for "transactional flow" system design

Copy this checklist; it fits checkout, ride-booking, seat reservation, ticket sales, money transfer, etc.

```
1. FRAME
   - Restate the flow as: reserve a scarce resource → charge → commit → async follow-up.
   - Functional + non-functional reqs. State: correctness > latency.
   - Scope explicitly (what you'll skip).

2. API
   - Single write endpoint, POST, with a client-supplied Idempotency-Key header.
   - Define request/response + error codes (409 in-progress, 422 key-reuse mismatch).

3. IDEMPOTENCY
   - Idempotency store keyed by K, UNIQUE constraint = concurrency guard.
   - States: IN_PROGRESS / COMPLETED; store & replay the response; hash the body; TTL.
   - Propagate the key to downstream side-effecting services (payment PSP).

4. CONCURRENCY ON THE SCARCE RESOURCE
   - Pick: pessimistic lock → optimistic conditional update → reservation+TTL → Redis counter.
   - Default = reservation + atomic conditional decrement. Justify vs contention level.
   - Guarantee: the "cannot go negative" check lives in the atomic write (WHERE avail >= qty).

5. DISTRIBUTED TRANSACTION
   - Saga (orchestrated) with compensations for each step.
   - Transactional Outbox for reliable event emission (no dual-write bug).
   - at-least-once delivery + idempotent consumers = effectively-once.

6. SYNC vs ASYNC SPLIT
   - Sync: validate, reserve, authorize, persist, return.
   - Async (event-driven): capture, fulfill, notify, analytics.

7. STATE MACHINE
   - Enumerate order/entity states + legal transitions; every transition idempotent & audited.

8. FAILURE MODES
   - Client retry, service crash mid-saga, payment timeout, reservation orphan, poison message.
   - Answers: idempotency, compensations, TTL sweeper, retries+backoff+jitter, DLQ.

9. SCALE & OPS
   - Hot-key handling (Redis/sharding), partitioning by user/SKU, rate limiting, fraud.
   - Observability: trace idempotency key, oversell/auth-failure/expiry metrics.

10. TRADE-OFFS
   - CAP stance per component; consistency vs latency; complexity vs correctness.
```

---

**If I had to compress the whole answer to 4 sentences for the interviewer:**
1. Client sends a unique **idempotency key**; a **UNIQUE-constraint insert** makes the operation exactly-once and replays the stored response on retry.
2. Inventory uses a **reservation with a TTL + an atomic conditional decrement** (`WHERE available >= qty`) so overselling is structurally impossible and hot SKUs can be fronted by a **Redis atomic counter**.
3. The cross-service flow is a **Saga with compensations**, and events are emitted via a **transactional outbox** so at-least-once delivery + idempotent consumers gives effectively-once.
4. The synchronous path only reserves + authorizes; **capture and fulfillment are async** and eventually consistent.
