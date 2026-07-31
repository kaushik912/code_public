This is a great thing to theorize, because the answer separates a clean design from a tangled one. Let me build the framework in two layers: **(1) the invariant that never changes**, and **(2) the transport choices that vary**.

## Layer 1: the invariant — separate "the fact" from "the transition"

The single most important principle:

> A participant reports **what happened to it** (a fact/outcome). It does **not** decide or write the orchestrator's next state. Interpreting that fact into a state transition is the **orchestrator's** job alone.

So when `chargePayment` succeeds, the participant emits the **fact** `PaymentCharged`. It must **not** reach into the saga and set `state = INVENTORY_PENDING`. Why this matters:

- **Ownership.** The Payment Service owns *payment* facts. The orchestrator owns *the flow*. If the participant writes the orchestrator's state, you've coupled two services' internals and there's no longer a single owner of the flow — the exact debuggability nightmare from the choreography discussion.
- **Reusability.** The same `PaymentCharged` fact can drive *many* different sagas/orchestrators. If the participant hardcodes "advance saga X to state Y," it can only ever serve saga X.

So option (c) as you phrased it — "the participant updates the *saga's* DB state" — is the **anti-pattern**. But there's a version of (c) that's correct, which I'll get to.

## Layer 2: what the participant does internally (always the same)

Regardless of transport, the participant's local transaction does **two** things atomically (this is the outbox again):

```
[TX] {
   update MY OWN state   -> payment row = CHARGED     (the participant's data)
   record MY OUTCOME     -> "PaymentCharged" fact       (to be delivered somehow)
}
```

It updates **its own** database (payment = charged) — that's legitimate and necessary. What it does *not* touch is the orchestrator's `saga_instance` table. The outcome then travels to the orchestrator by one of three transports:

## The three transports (this is your (a)/(b)/(c))

| | Mechanism | Coupling | Push/Pull | When |
|---|---|---|---|---|
| **A. Reply message** | Publish `PaymentCharged` to a reply queue/topic; orchestrator consumes | **Loosest** — participant knows only a topic name, not the orchestrator | Push | Async systems, Kafka/Rabbit already present |
| **B. Callback / webhook** | Participant does `POST /saga/{id}/events` on the orchestrator's API | **Tighter** — participant must know the orchestrator's URL | Push | Sync HTTP shops, no broker, external providers (Stripe webhooks!) |
| **C. Shared/observable state** | Participant writes its own outcome to a store; orchestrator **polls/reads** it | **Loosest logically, but shared infra** | Pull | Polling designs, or when participant can't reach out |

Then, in **all three**, the orchestrator does the *same* thing on receipt:

```
orchestrator receives fact "PaymentCharged"
  → look up transition (current state + fact) in the state machine
  → [TX] update saga_instance state + enqueue next command (outbox)
```

## The clean way to say it

The key theoretical decomposition is **three distinct responsibilities**, and your question is really "where does the boundary between step 2 and 3 sit?":

1. **Do the work + record own outcome** — participant, atomically (its DB + outbox).
2. **Transport the outcome** — message / webhook / polled state (this is A/B/C; interchangeable).
3. **Interpret outcome → transition + next command** — orchestrator, atomically (saga DB + outbox).

The participant owns 1. The orchestrator owns 3. **2 is just plumbing** and is the *only* thing that actually varies. Your three candidate behaviors aren't really alternatives for "what the action does" — they're three implementations of **step 2 only**. Steps 1 and 3 are invariant.

## So, directly answering your three:

- **"Publish a reply message `payment_charged`"** → ✅ transport A. The participant emits a *fact*, orchestrator decides the transition. Cleanest, loosest coupling.
- **"Call a POST API (post-action hook)"** → ✅ transport B. Same fact, delivered over HTTP instead of a queue. Valid; tighter coupling (participant knows orchestrator's address). This is literally how Stripe/PayPal webhooks work.
- **"Update the DB state with this value"** →
  - If it means *update the participant's own payment record to CHARGED* → ✅ **required**, that's step 1, happens regardless.
  - If it means *update the orchestrator's saga state directly* → ❌ **anti-pattern** — breaks ownership; the participant would be doing the orchestrator's job (step 3). The correct "DB" version is transport C: write the *outcome* somewhere the orchestrator *polls*, and let the orchestrator do the transition.

## The one-line theory

> A saga step's completion has three separable concerns — **perform-and-record-own-outcome** (participant), **transport-the-outcome** (message / webhook / polled state — interchangeable), **interpret-outcome-into-a-transition** (orchestrator). The participant emits a *fact*, never a *transition*. Everything you listed is a choice of *transport* only; the ownership boundary stays fixed.

That framing — "the participant reports facts, the orchestrator owns transitions, transport is pluggable" — is the theorization you're after, and it's exactly why frameworks like Temporal can swap the transport (queue vs poll vs callback) without your saga logic changing.


Yes, your instinct is right — a webhook **is** just an HTTP API call. The twist is *who calls whom*. Let me give you the precise semantics.

## The core definition

> A webhook is a **reversed API call**: instead of *you* calling a server to ask "is it done yet?", the server calls *you* when it's done.

That's the whole idea. It's sometimes called a **"reverse API"** or an **"HTTP callback."** Same HTTP POST you already know — the direction of initiation is flipped.

## Normal API vs webhook

**Normal API (you initiate — "pull"):**
```
You  ──── GET /payment/123/status ───▶  Payment provider
You  ◀──── "still processing" ─────────  
You  ──── GET /payment/123/status ───▶   (poll again...)
You  ◀──── "still processing" ─────────
You  ──── GET /payment/123/status ───▶   (and again...)
```
You have to keep asking. Wasteful, laggy — this is **polling**.

**Webhook (they initiate — "push"):**
```
(you registered your URL once, ahead of time)
...time passes, you do nothing...
Payment provider ──── POST https://you.com/hooks/payment ───▶  You
                       body: { "event": "payment.charged", "id": "123" }
You ──── 200 OK ─────────────────────────────────────────────▶
```
They call *your* endpoint the moment the event happens. No polling. This is **push**.

## The semantics / lifecycle

A webhook has four distinct phases — this is the "exact semantics" you asked for:

1. **Registration (once, up front).** You tell the provider: "when event X happens, POST to *this URL* of mine." Either via their dashboard (Stripe/GitHub settings) or an API call. This is the critical difference from a plain callback — the caller learns your address **ahead of time**, not per-request.

2. **Event occurs.** Something happens on their side — payment settles, a git push lands, a build finishes.

3. **Delivery.** The provider makes an **HTTP POST to your registered URL**, with the event details in the body (usually JSON). Your endpoint is a normal REST endpoint — nothing special about it except that *they* are the client.

4. **Acknowledgment.** You return **`200 OK`** to say "got it." If you return an error or time out, the provider will typically **retry** (which is why webhook handlers must be **idempotent** — the same event may arrive twice).

## So, precisely answering your question

> "Is it just an API call when a process is done with its task?"

**Almost exactly** — with two refinements:

- It's an API call **made *to you*, by the system that did the work** (not one you make to them).
- It requires **prior registration** — they can only call you because you told them your URL in advance. Without that registration step, it's just an arbitrary callback; the "webhook" concept is specifically *the pre-arranged, event-triggered reverse call*.

## Why it exists (the "why" makes the semantics stick)

Polling is wasteful and slow: you either poll too often (burning requests on "not yet") or too rarely (laggy). Webhooks invert it — **zero requests while nothing happens, one request the instant it does.** It's **event-driven push over HTTP.**

## How it ties back to our saga conversation

Remember transport option **B** ("participant calls a POST API")? That **is** a webhook:

- In the saga, when Payment finishes charging, it POSTs `PaymentCharged` to the orchestrator's `/saga/{id}/events` endpoint. Payment is the *caller*, orchestrator is the *callee* — reversed from the original command call.
- Real-world example: **Stripe/PayPal**. You call *their* API to start a charge (normal API). But payment settlement is async and can take time, so they call *your* webhook when it finalizes (`payment_intent.succeeded`). That webhook is exactly transport B delivering the "fact" back to your orchestrator.

And the caveats we already discussed apply directly to webhooks:
- **Idempotency** — retries mean duplicate deliveries; dedupe on the event id.
- **Signature verification** — since anyone could POST to your public URL, providers sign the payload (e.g. Stripe's `Stripe-Signature` header) so you can verify it genuinely came from them. This is the one security wrinkle webhooks add over a normal API.

## One-line mental model

> A normal API call = **"I call you to ask."** A webhook = **"you call me to tell,"** using a URL I registered with you in advance. Same HTTP POST — opposite direction, event-triggered, push instead of poll.

So in the saga's command/reply, a webhook is simply the **reply** delivered as an inbound HTTP call instead of a queue message.


Let me give concrete, real-world examples for each of the three transports, then a decision lens for picking.

## Transport A — Reply message (async queue/event bus)

The outcome is published to a broker; the consumer picks it up.

**Real examples:**
- **Kafka** `payment.replies` topic — orchestrator consumes. (LinkedIn, Uber, most high-throughput shops.)
- **RabbitMQ / ActiveMQ** reply queues — classic enterprise messaging.
- **AWS SQS / SNS** — SNS fans an event out, SQS queues it for the consumer.
- **Google Pub/Sub, Azure Service Bus** — cloud-native equivalents.
- **Temporal activity completion** — internally this is the model (durable task queue).

**Best when:**
- High throughput / spiky load — the queue **buffers** bursts so consumers aren't overwhelmed.
- You want **loosest coupling** — participant knows only a topic name.
- Multiple consumers need the same event (fan-out).
- The two services have **different availability** — if the orchestrator is down, the message waits in the queue instead of being lost.
- You need **durability/replay** — Kafka keeps the log.

**Weak when:** you don't already run a broker (operational overhead), or you need a synchronous answer *right now* in a request/response cycle.

## Transport B — Webhook / HTTP callback (push)

The participant POSTs the outcome to the orchestrator's URL.

**Real examples:**
- **Stripe / PayPal** payment webhooks (`payment_intent.succeeded`) — the canonical case; settlement is async, they call you back.
- **GitHub webhooks** — push/PR events POST to your CI.
- **Twilio** — SMS/call status callbacks.
- **Slack Events API**, **Shopify** order webhooks, **CI/CD** deploy-complete callbacks.

**Best when:**
- Crossing an **organizational boundary** — you can't make an external SaaS publish to *your* Kafka, but they can POST to your public URL. This is *the* reason webhooks dominate third-party integrations.
- You have **no message broker** and don't want to run one — HTTP is universal.
- Events are **low-to-moderate volume** and you want near-real-time push without polling.

**Weak when:**
- The receiver is **down** during delivery — you depend on the sender's retry policy, and delivery guarantees are weaker than a durable queue.
- **Very high volume** — a POST per event can hammer the receiver (no built-in buffering; queue is better).
- Receiver isn't publicly reachable (webhooks need an inbound-accessible endpoint).

## Transport C — Shared / polled state (pull)

The participant writes its outcome to a store; the orchestrator polls or reads it.

**Real examples:**
- **Database polling** — participant sets `payment.status = CHARGED`; a scheduler scans for changes. (Your outbox *relay* is exactly this pattern.)
- **S3 / object-store markers** — write a `job-123.done` file; watcher polls the bucket. Common in **data pipelines / batch ETL**.
- **Redis / cache flag** polled by the orchestrator.
- **Cron/batch reconciliation jobs** — nightly "find all payments marked captured but orders not confirmed."
- **AWS Step Functions polling pattern** (`waitForTaskToken` with polling) for long-running jobs.

**Best when:**
- The participant **can't reach out** (locked down, no outbound network, or a legacy batch system that only writes to a DB/file).
- **Long-running / batch** work where near-real-time isn't needed (ETL, report generation, nightly settlement).
- You want a **reconciliation safety net** even if you primarily use A or B — polling catches the events that a message drop or a failed webhook missed. (This is why serious systems use C *alongside* A/B.)

**Weak when:** you need low latency (polling adds delay), or high frequency (polling wastes cycles asking "anything yet?").

## Decision lens — pick by asking 3 questions

| Question | Points to |
|---|---|
| **Is it inside my system or across an org boundary?** | Inside → A (queue). External SaaS → B (webhook) — they can't touch your broker. |
| **What's the volume/latency?** | High volume / spiky → A (buffers). Low volume, real-time → B. Batch / not-urgent → C. |
| **Can the participant even initiate a call?** | Yes → A or B. No (locked-down/legacy/batch) → C (they write, you poll). |
| **Do I need durability & replay?** | Yes → A (Kafka log) or C (DB is the record). Webhook alone → weakest. |

## The practical real-world answer

Mature systems don't pick *one* — they **layer**:

- **A (queue)** for internal, high-throughput saga steps → decoupling + buffering.
- **B (webhook)** at the **edges**, for third-party providers (Stripe, PayPal, GitHub) that can only reach you over HTTP.
- **C (polling reconciliation)** as the **safety net** underneath both — a periodic job that catches anything a dropped message or a failed webhook missed. This is why you'll see "we process Stripe webhooks **and** run a nightly reconciliation poll against Stripe's API" — belt and suspenders.

## One-line summary

> **Inside your system, high volume → message queue (A).** **Across an org boundary / third-party → webhook (B).** **Long-running, locked-down, or as a safety net → polled state (C).** Serious systems use B at the edge, A in the core, and C underneath to catch what the other two drop.

That layering — queue in the core, webhooks at the boundary, polling as reconciliation — is the answer that shows you've seen these fail in production, not just read about them.
