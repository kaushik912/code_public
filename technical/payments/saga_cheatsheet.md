# SAGA — One-Page Interview Cheat-Sheet

## The 5 keywords (memorize these; derive the rest)
**Local transactions · Compensation · Orchestration/Choreography · Idempotency · Persistence (+Outbox)**

## Why SAGA exists (opening line)
> "Across microservices with separate DBs, there's no distributed ACID. 2PC is blocking and doesn't scale. So I trade atomicity for a **sequence of local transactions, each with a compensating action** to undo it on failure."

## The one real decision: Orchestration vs Choreography
| | Orchestration | Choreography |
|---|---|---|
| How | central coordinator directs each step | services react to each other's events |
| Best for | complex/linear flows, need visibility | many services, loose coupling |
| Pro | flow in one place, debuggable | decoupled, scales |
| Con | central coordinator | flow scattered, hard to trace |
| Debug | read the state machine | need correlation-id + tracing + event log |

**Rule of thumb:** few services / need clarity → orchestrate. Many services + committed to observability → choreograph.

## The non-negotiable gotchas (what separates seniors)
- **Compensation ≠ rollback** — it's a *semantic undo* (refund, not un-charge; apology, not un-send).
- **Idempotency** — at-least-once delivery ⇒ dedupe on an idempotency key; on a duplicate, **re-send the cached reply**, don't redo the work.
- **Persist saga state** — coordinator crash ⇒ recover from DB, not memory.
- **No isolation** — others see `PENDING` state (dirty reads); mitigate with status flag / semantic lock.
- **Order steps by cost-of-compensation** — do the irreversible step **last** (authorize→...→**capture**), so most failures *void a hold* not *refund a capture*.

## Reliability mechanics
- **Transactional Outbox** — write state change + outgoing command in the **same local DB transaction**; a relay (polling publisher) publishes to the broker. Closes the "crashed between DB-write and message-send" gap.
- **Dead-letter queue** — for sagas that fail past max retries → alert + manual investigation.
- **Retry transient failures first** (max attempts + exponential backoff) **before** compensating.

## Command/reply theory
Three separable concerns:
1. **Perform + record own outcome** — *participant*, atomically (its own DB + outbox).
2. **Transport the outcome** — pluggable (see below).
3. **Interpret outcome → transition + next command** — *orchestrator*, atomically.

> Participant emits a **fact** (`PaymentCharged`), never a **transition**. Transitions belong to the orchestrator.

## Transport choices (this is just concern #2)
| Transport | Example | Best when |
|---|---|---|
| **A. Queue** (message) | Kafka, SQS/SNS, Rabbit | inside system, high volume, loose coupling, replay |
| **B. Webhook** (HTTP push) | Stripe/PayPal/GitHub callbacks | across org boundary, no broker, low-moderate volume |
| **C. Polled state** (pull) | DB poll, S3 marker, cron reconcile | long-running/batch, locked-down participant, safety net |

**Layered real answer:** queue in the core (A), webhook at the edge (B), polling reconciliation underneath (C).

**Webhook =** reversed API — *they* POST to a URL you registered in advance. Push, not poll. Needs idempotency + signature verification.

## Where transitions are defined
Not in scattered `switch`/`setState` — pull into an **explicit transition table** `(from, event → to, command)` or a **state-machine library**. Transport (outbox/queues) and transition logic are **orthogonal concerns**.

## Frameworks (don't lead with these; offer when asked)
- **Temporal** — durable execution; saga as **sequential code**, `Saga.addCompensation()`, declarative `RetryOptions`. Engine handles state/retries/crash-recovery. *(Gold standard.)*
- **AWS Step Functions** — managed, JSON state machine.
- **Camunda/Zeebe** — BPMN.
- **Spring-native:** Eventuate Tram Saga, Axon (`@Saga`), Seata (SAGA/TCC). *Spring Statemachine* = state modeling only, you own persistence.
- Spring core has **no** built-in saga.

## Async note (Temporal)
Sequential-looking activity calls are **non-blocking but ordered** (like JS `await`) — waiting workflow is dehydrated, holds no thread. For true concurrency use `Async.function` → `Promise` (`Promise.allOf`/`anyOf` = `Promise.all`/`race`). Only parallelize **independent** steps; must use Temporal's deterministic `Promise`, not `CompletableFuture`.

## Closing soundbite (land this)
> "An orchestrated saga with per-instance state persisted in a DB, driven over command/reply. Reliability = retries-with-backoff before compensating, idempotent consumers keyed by an idempotency id, and a transactional outbox so state and command publish atomically. In production I'd run it on Temporal rather than hand-roll durable recovery — but I'd still own step-ordering and idempotency keys to external providers, which the engine can't reason about."

---

Want me to save this as a markdown file you can keep, or turn it into a printable one-page PDF?
