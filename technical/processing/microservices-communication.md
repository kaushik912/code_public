Good topic. Let me build this up in three layers, keeping to the underlying ideas rather than any one vendor's spelling of them.

## 1. How two services talk — the core axes

Don't memorize a list of protocols. There are really only **two independent decisions**, and everything else is a point in that space.

**Axis A: Synchronous vs. Asynchronous** (does the caller wait?)

**Axis B: Point-to-point vs. Brokered** (does the caller know who receives it?)

| | Point-to-point | Through a broker |
|---|---|---|
| **Synchronous** (caller blocks for a reply) | REST/HTTP, gRPC, GraphQL | (rare — request/reply over a queue) |
| **Asynchronous** (fire and continue) | webhooks | message queue / event bus (Kafka, SQS, RabbitMQ) |

The invariant idea:

- **Synchronous** = *temporal coupling*. Both services must be alive at the same instant. Simple to reason about ("call function, get answer"), but the caller inherits the callee's latency and failures. A slow downstream service becomes *your* slow service. This is where retries, timeouts, and circuit breakers live.

- **Asynchronous** = *you trade immediacy for decoupling*. Producer drops a message and moves on; consumer processes whenever. The broker absorbs bursts (backpressure) and outages (the consumer can be down and catch up later). Cost: you lose the neat "get an answer back" — you now reason about eventual consistency, ordering, duplicate delivery, and "where did my message go."

Two sub-distinctions worth naming because people conflate them:

- **REST vs gRPC** is *not* a fundamental difference — both are synchronous point-to-point RPC. gRPC is just "RPC with a strict binary contract (protobuf) and HTTP/2 multiplexing." Pick gRPC for internal service-to-service where you control both ends and want speed + a typed contract; REST for public/edge APIs where ubiquity and human-debuggability matter.

- **Queue vs. Event stream.** A *queue* (SQS, RabbitMQ) is "a task for someone to do" — usually one consumer, message deleted after handling (command semantics). An *event log* (Kafka) is "a fact that happened" — many independent consumers each read at their own offset, and the log is retained (event semantics). Same transport family, opposite mental models: **command = "do this," event = "this happened."**

**The one rule that matters:** prefer async/events for anything that doesn't need an immediate answer. Every synchronous hop you add to a request path multiplies your failure surface and adds its latency to your tail.

---

## 2. Orchestration — and its twin, choreography

Once a business action spans several services (e.g. "close an opportunity" → recalc ARR → update rollups → notify), you need to coordinate them. Two philosophies:

**Orchestration** — one central brain (an *orchestrator* / *saga coordinator*) that explicitly calls each step and decides what's next.

```
          ┌─────────────────┐
          │  Orchestrator   │   knows the whole workflow
          └───┬────┬────┬───┘
        1.    │ 2. │ 3. │
     ┌────────┘    │    └────────┐
     ▼             ▼             ▼
 ┌───────┐    ┌────────┐    ┌─────────┐
 │ ARR   │    │Rollup  │    │ Notify  │   each dumb about the others
 └───────┘    └────────┘    └─────────┘
```

- The logic lives in **one place** — easy to see the flow, easy to add a step, easy to reason about compensation.
- The orchestrator is a coupling point and a potential bottleneck/SPOF.
- Tools that *are* this idea: Temporal, AWS Step Functions, Camunda. They're really "a durable state machine that survives restarts and remembers where each workflow instance is."

**Choreography** — no brain. Each service emits events; others react. The workflow is *emergent* — nobody owns it end-to-end.

```
 ┌───────┐  OpportunityClosed   ┌────────┐  ArrRecalculated  ┌─────────┐
 │ Oppty │ ───────────────────► │  ARR   │ ────────────────► │ Rollup  │ ─► ...
 └───────┘      (event bus)     └────────┘                   └─────────┘
```

- Maximally decoupled, scales well, no central bottleneck.
- But the workflow exists only in everyone's heads — hard to answer "what's the full sequence?" and hard to debug ("why didn't step 3 fire?").

**The Saga pattern** applies to both: since you can't have a distributed ACID transaction across services, you break the operation into local transactions, each with a **compensating action** to undo it if a later step fails. Orchestration-based saga = the coordinator issues the compensations. Choreography-based saga = each service listens for a failure event and rolls itself back.

**Rule of thumb:** orchestration when the workflow is complex, long-lived, or needs auditability/visibility (money, approvals, multi-step recalcs — sounds like your ARR pipeline). Choreography when steps are simple, independent, and you value decoupling over a legible end-to-end story.

---

## 3. Service mesh — moving the plumbing out of your code

Notice that everything in section 1 (retries, timeouts, circuit breaking, mTLS, load balancing, tracing) is **the same non-business logic every service re-implements.** A service mesh's entire premise: *stop putting that in application code.*

**The mechanism — the sidecar:** next to each service instance runs a proxy (Envoy is the common one). Your service talks only to `localhost`; the proxy intercepts all in/out traffic. Every service's proxy + a central control plane = the mesh.

```
   ┌──────────────── Pod A ────────────────┐        ┌──────────────── Pod B ────────────────┐
   │  ┌──────────┐        ┌────────────┐   │        │  ┌────────────┐        ┌──────────┐   │
   │  │ Service  │◄──────►│  Sidecar   │◄──┼── mTLS ─┼─►│  Sidecar   │◄──────►│ Service  │   │
   │  │  (ARR)   │ local  │  (proxy)   │   │        │  │  (proxy)   │ local  │ (Rollup) │   │
   │  └──────────┘        └────────────┘   │        │  └────────────┘        └──────────┘   │
   └───────────────────────────────────────┘        └───────────────────────────────────────┘
                     ▲                                              ▲
                     └──────────────┬───────────────────────────────┘
                            ┌────────────────┐
                            │ Control plane  │  (Istio/Linkerd): pushes policy,
                            │                │   certs, routing rules to every proxy
                            └────────────────┘
```

**Split it into two planes** (this is the concept to hold onto):

- **Data plane** = the sidecar proxies. They carry the actual traffic and *enforce* the rules.
- **Control plane** = the brain (Istio, Linkerd). It doesn't touch traffic; it *configures* all the proxies — pushes routing rules, TLS certs, policies.

**What you get for free, without touching app code:**
- **mTLS everywhere** — proxies encrypt + mutually authenticate every hop. Identity-based security instead of network-based ("this *is* the ARR service," not "this came from an allowed IP").
- **Traffic control** — canary/blue-green, retries, timeouts, circuit breaking as *config*, not code.
- **Observability** — since the proxy sees every call, you get uniform metrics, and distributed traces "for free."

**The honest tradeoff:** a mesh adds a proxy hop to every call (latency) and real operational complexity. It pays off at scale — many services, polyglot stacks, strict security/compliance. For a handful of services, a shared client library doing retries + timeouts is often enough, and you skip the operational tax.

---

### How the three connect

They're three heights of the same problem:

1. **Communication** = how one hop works.
2. **Orchestration** = how you compose many hops into a business workflow.
3. **Service mesh** = how you make *all* hops reliable and secure without rewriting that logic in every service.

Want me to go one level deeper on any single one — the saga compensation mechanics, Kafka's consumer-group/offset model, or how mTLS identity actually gets bootstrapped in a mesh? I'd rather drill one than skim all three.
