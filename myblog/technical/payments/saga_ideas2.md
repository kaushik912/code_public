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
