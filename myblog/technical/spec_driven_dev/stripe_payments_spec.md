# Payment Service — MVP Spec

Auth–capture payment backend for an e-commerce checkout, integrated with Stripe,
designed to scale horizontally and stay correct under retries and partial failures.

**Scope of this MVP:** card payments via Stripe, delayed capture at shipment,
SAGA-coordinated checkout, idempotency, and a double-entry ledger. Out of scope:
multi-provider routing, fraud/risk engine, multi-currency FX, subscriptions.

---

## 1. Goals & Non-Goals

### Goals
- Authorize funds at checkout, capture at shipment (days later).
- Correct under retries, duplicate webhooks, and crashes (idempotent + durable).
- Stateless services; scale by adding replicas.
- Auditable money movement (append-only double-entry ledger).
- Reconcile against Stripe as the source of truth.

### Non-Goals (MVP)
- Multiple payment providers / smart routing.
- Fraud scoring, 3DS step-up flows beyond what Stripe handles inline.
- Partial-capture across many shipments (support **one** capture; full or single partial).
- Multi-currency. Single currency (e.g. USD), minor units (cents), integer amounts.

---

## 2. Core Model

A payment is a **durable state machine**, not a request. Auth and capture are
separated by days, so nothing lives in memory or a request thread.

### Payment state machine
```
CREATED → AUTH_PENDING → AUTHORIZED → CAPTURE_PENDING → CAPTURED → SETTLED
              │              │                              │
              ↓              ↓ (void)                       ↓ (refund)
          AUTH_FAILED     VOIDED                        REFUNDED
```
Every transition: **durable write → emit event → (maybe) call Stripe**. Never reverse the order.

### Auth vs capture
- **Authorize** = Stripe places a hold. `PaymentIntent.create(capture_method='manual', confirm=true)`.
- **Capture** = pull the held funds at shipment. `PaymentIntent.capture()`.
- Holds expire (~7 days). A watchdog voids/alerts before expiry if not yet captured.

---

## 3. Architecture

```
Client (Stripe.js) → API Gateway → Order Service → Payment Service → Stripe
                                          │               │             │
                                    Saga Orchestrator   Postgres     Webhooks
                                          │            (payments,        │
                                          │             outbox,     → ingest queue
                                       Kafka/SQS        ledger)          │
                                          │             Redis      → Payment Service
                                     (event bus)   (idempotency)
```

Services are **stateless**. All state lives in Postgres / Redis / the event bus.

---

## 4. Components

| Component | Responsibility |
|---|---|
| **Payment Service** | Owns payment lifecycle, talks to Stripe, writes ledger. Stateless. |
| **Saga Orchestrator** | Drives checkout across Inventory → Payment → Order; owns compensations. |
| **Postgres** | `payments`, `outbox`, `ledger_entries`, `idempotency_keys`, `saga_state`. |
| **Redis** | Idempotency cache, rate limits. |
| **Event bus** (Kafka/SQS) | Async fan-out for capture, notifications, recon. |
| **Outbox relay** (Debezium/CDC) | Publishes outbox rows to the bus (no dual-write race). |
| **Webhook ingester** | Verifies Stripe signatures, enqueues events, acks fast. |

---

## 5. Data Model (MVP tables)

```sql
-- Payment lifecycle
payments (
  id              uuid pk,
  order_id        uuid not null,
  user_id         uuid not null,
  amount_minor    bigint not null,        -- cents
  currency        char(3) not null,
  status          text not null,          -- CREATED..REFUNDED
  stripe_intent_id text,
  auth_expires_at timestamptz,
  created_at      timestamptz,
  updated_at      timestamptz
);

-- Transactional outbox (written in same tx as the state change)
outbox (
  id           uuid pk,
  aggregate_id uuid not null,             -- payment id
  event_type   text not null,            -- PAYMENT_AUTHORIZED, PAYMENT_CAPTURED...
  payload      jsonb not null,
  published    boolean default false,
  created_at   timestamptz
);

-- Append-only double-entry ledger
ledger_entries (
  id          uuid pk,
  txn_id      uuid not null,              -- groups the debit+credit
  account     text not null,             -- e.g. 'user:{id}', 'stripe:holding', 'revenue'
  direction   text not null,             -- 'DEBIT' | 'CREDIT'
  amount_minor bigint not null,
  payment_id  uuid not null,
  created_at  timestamptz
  -- INVARIANT: sum(debits) == sum(credits) per txn_id
);

-- Idempotency: request key -> stored result
idempotency_keys (
  key         text pk,
  scope       text not null,             -- 'authorize' | 'capture' | 'webhook'
  response    jsonb,
  status      text not null,             -- IN_PROGRESS | DONE
  created_at  timestamptz
);

-- Saga persistence
saga_state (
  id          uuid pk,
  order_id    uuid not null,
  step        text not null,             -- current step
  status      text not null,             -- RUNNING | COMPENSATING | DONE | FAILED
  context     jsonb,
  updated_at  timestamptz
);
```

Ledger is **append-only** — no mutable balance column. Balance = sum of entries.
Shard `payments` / `ledger_entries` by `user_id` when a single node is no longer enough.

---

## 6. Checkout SAGA (orchestrated)

One orchestrator owns the money state. Each step has a compensation.

| Step | Forward action | Compensation |
|---|---|---|
| 1 | Reserve inventory | Release inventory |
| 2 | **Authorize payment** | **Void authorization** (release hold) |
| 3 | Confirm order | Cancel order |
| (later) | Capture at shipment | Refund (if already captured) |

Rules:
- **Compensations are forward-only semantic reversals** — captured money is *refunded*, not rolled back.
- **Saga state is a DB row** — survives crashes, resumes from `step`.
- **Timeouts drive compensation** — a watchdog scans stuck sagas and expiring auths.

---

## 7. API (MVP)

All mutating endpoints require an `Idempotency-Key` header.

```
POST /payments/authorize
  body: { orderId, userId, amountMinor, currency, paymentMethodId }
  → 201 { paymentId, status: "AUTHORIZED" }        (idempotent)

POST /payments/{id}/capture
  body: { amountMinor? }                            (defaults to full)
  → 200 { paymentId, status: "CAPTURED" }           (idempotent)

POST /payments/{id}/void
  → 200 { paymentId, status: "VOIDED" }

POST /payments/{id}/refund
  body: { amountMinor? }
  → 200 { paymentId, status: "REFUNDED" }

GET  /payments/{id}
  → 200 { payment + ledger summary }

POST /webhooks/stripe                               (signature-verified, async)
  → 200 (ack fast; process off queue)
```

---

## 8. Correctness Requirements

These are the non-negotiables; the MVP is wrong without them.

1. **Idempotency on every external + mutating call.** Pass Stripe's `Idempotency-Key`
   through; store request-key → result. Retries/duplicates are no-ops that return the cached result.
2. **Transactional outbox.** State change + event written in **one** local transaction;
   CDC relay publishes. Never "write DB then publish" (dual-write race).
3. **Webhooks are the source of truth.** Verify signatures. Reconcile any drift between
   your synchronous response and Stripe's async event.
4. **Order of operations:** durable state write happens **before** the Stripe call is
   marked complete; recovery reconciles the "called Stripe but DB write failed" gap via webhook.
5. **Watchdog job.** Scans for expiring auths (void/alert) and stuck sagas (compensate).
6. **Double-entry invariant.** Every money movement posts a balanced debit+credit under one `txn_id`.

---

## 9. Scaling Approach

- **Stateless services** → scale by adding replicas behind the gateway.
- **Async after auth** — only authorize is synchronous (user waits). Capture, notifications,
  ledger fan-out, recon all run off queues; backpressure absorbs Stripe latency/outages.
- **Sharded, append-only ledger** by `user_id` → no lock contention, full audit trail.
- **Redis idempotency cache** with Postgres fallback.
- **Circuit breaker + exponential backoff** around Stripe; **DLQ** for poison events.

---

## 10. Failure Scenarios (must handle)

| Scenario | Handling |
|---|---|
| Double checkout click | Idempotency key → single auth, cached response. |
| Duplicate Stripe webhook | Dedup by event id; processing is a no-op replay. |
| Crash after Stripe auth, before DB commit | Webhook reconciles; recon job repairs state. |
| Capture never arrives, auth nears expiry | Watchdog voids hold and/or alerts. |
| Stripe outage | Retries w/ backoff; circuit breaker; queued events drain on recovery. |
| Capture succeeds at Stripe, DB write fails | Webhook (`payment_intent.succeeded`) drives state to CAPTURED. |
| Partial shipment | Partial capture; release remainder (single partial in MVP). |

---

## 11. Observability

- **Metrics:** auth success rate, capture latency, webhook lag, DLQ depth, saga compensation rate.
- **Recon job:** nightly diff of `ledger_entries` vs Stripe balance report; alert on drift.
- **Structured logs** keyed by `paymentId` / `orderId` / `sagaId`.

---

## 12. Minimal Build Order

1. `payments` table + state machine + `/authorize` (manual capture) with idempotency.
2. Ledger (double-entry) posting on auth/capture.
3. Outbox + CDC relay + event bus.
4. `/capture`, `/void`, `/refund`.
5. Stripe webhook ingester + reconciliation.
6. Saga orchestrator + compensations + watchdog.

That sequence is always correct at each step: state is durable and idempotent from step 1,
async fan-out arrives at step 3, and the saga ties services together last.
