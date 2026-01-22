Nice — great list. I’ve answered each point directly (kept answers compact and interview-friendly). After this I’ll give a few one-line “hint/cheat” sentences you can glance at before solving or explaining a problem in an interview.

---

# System design: 1M requests/hour, JSON with 10–15 fields, client wants status "tomorrow"

**Targets / numbers**

* 1M req/hour ≈ **278 req/sec** (steady). If bursts, design for higher peak (x2–3).
* Plan for throughput, availability, and eventual consistency for “status tomorrow”.

**High-level architecture**

1. **API layer**: API Gateway / LB → autoscaled stateless app servers (Spring). Enforce auth, rate limits, request validation.
2. **Ingestion queue**: Accept request quickly and **ACK** to client with a requestId. Push payload to durable message broker (Kafka/RabbitMQ/SQS).

   * Use **partition key = clientId or requestId** to preserve ordering if needed.
3. **Processing workers**: Consumer pool reads from broker, performs validation/processing, and writes results to DB in **batches**.
4. **Storage**:

   * **Primary DB** for request metadata/status (OLTP) — partitioned/sharded by clientId or time. Use a write-optimized store (e.g., Postgres with partitioning, DynamoDB).
   * **Cold/archive store** for full payloads (S3 + index) if payloads large and rarely read.
5. **Status retrieval**:

   * Client gets `requestId` on submit; status endpoint reads current status from DB (or cache) for “tomorrow”.
   * Also offer **webhook / callback** or send notification when processing completes (better than polling).
6. **Observability**: metrics, tracing, alerts, and dead-letter queue (DLQ) for failing messages.

**Will caching help?**

* Yes for **status reads** (many reads per statusId). Use short TTL cache (Redis) to reduce DB load.
* Be careful: **high cardinality** (millions of unique IDs) reduces cache hit rate — caching helps only if same IDs are read often.
* For clients that poll same IDs repeatedly: use caching + conditional GET (ETag/If-Modified-Since) or push-based notifications.

**If client script sends many IDs / 1M/day**

* Encourage **batching on client**: allow endpoints that accept arrays of IDs (bulk submit) to amortize HTTP overhead.
* Server: support bulk ingest and use **bulk writes** into DB for efficiency.

**How to handle writes to DB**

* **Don’t write synchronously per request** (slow): use buffered / batched writes from worker consumers.
* Pattern: consumer accumulates N records or T ms then bulk insert (use DB bulk insert / COPY / batch API).
* Ensure idempotency: include `requestId` primary key or unique index to dedupe replays.

**Durability / Ordering / Exactly-once**

* Use Kafka (at-least-once) and implement **idempotent consumers** (unique constraint, upserts).
* If ordering is required per client, partition by clientId.

**Failure / retries**

* DLQ for poison messages.
* Circuit breakers and backpressure (HTTP 429) at API gateway.

**Scaling**

* Autoscale app servers, consumers, and DB read replicas.
* Monitor consumer lag; increase partitions if consumers are bottleneck.

**When to use SAGA**

* For distributed multi-service workflows where each step is separate service and compensations needed — SAGA choreography or orchestration fits.
* For single DB + services, prefer **transactional outbox** + message broker to guarantee delivery.

---

# Short answers to your specific Spring / Kafka / DB questions

1. **Spring singleton bean: can I clone and use it? How to safeguard?**

   * By default Spring `singleton` scope = one instance per container. Cloning a singleton is unusual. Better options:

     * Use **prototype** scope for per-use instance (inject `ObjectFactory<T>` or `Provider<T>`).
     * If you must copy a singleton, implement `Cloneable` or a copy/`copyConstructor`, but watch thread-safety and shared mutable state.
   * Safeguards: prefer immutable state in singletons; avoid shared mutable fields, or synchronize access. Use prototype beans for per-request state.

2. **Kafka: one topic, 2 partitions, each partition having 4 consumers; all consumers in same consumer group — how many consumers receive messages?**

   * **Only 2 consumers** (at most one consumer per partition in that consumer group) will be assigned partitions and receive messages. The other 6 (assuming 8 total?) will be idle.
   * If you need more parallelism, increase partitions. If consumers are in **different consumer groups**, each group receives a full copy of messages.

3. **Spring transaction and modifying an entity without calling save — any warning?**

   * If the entity is **managed** (attached to persistence context / Hibernate) and you modify it inside a transaction, changes are **automatically flushed** at commit — no explicit `save()` needed and Spring/Hibernate will not warn.
   * If the entity is **detached**, modifications are not tracked — you must `save()`/`merge()` or reattach, otherwise no DB update occurs.

4. **Using PUT for create operations in Spring — will it throw a runtime warning?**

   * No runtime warning. HTTP semantics: `PUT` is allowed for create **if** the client defines the resource URI and operation is idempotent. `POST` is typically used for server-assigned IDs. Spring will accept both unless you add custom validation. Use whichever matches your API semantics.

5. **How do you handle DB migrations? Asked about Flyway.**

   * Use **Flyway** or **Liquibase** for versioned migrations stored in repo and applied in CI/CD. Best practices:

     * Keep migrations **idempotent** and versioned.
     * Use **backward-compatible changes**: add new nullable columns, populate in background, switch app to use new column, then remove old column in later rollout.
     * For large data transformations, do **online migrations**: run migrations in batches, use feature flags, separate schema changes from data migrations.
     * Use **transactional migrations** where supported; test in staging; have rollback planning. For zero-downtime, prefer expand-contract pattern.
     * Consider **pt-online-schema-change** (Percona) or native DB online DDL features for big tables.

---

# Additional patterns & tips (practical interview points)

* **Outbox pattern**: ensure DB write + event publish atomicity — write event to outbox table within transaction; a relayer publishes it to broker.
* **Backpressure & throttling**: return 429 or queue locally; prioritize critical traffic.
* **Idempotency keys**: any endpoint that can be retried should accept idempotency key to dedupe.
* **Monitoring**: expose consumer lag, processing latency, error rates; SLAs.
* **Security**: client scripts should authenticate (API key), have per-client quotas.

---

# One-line interview “hint” sentences (cheat/hint before solving)

* **Design throughput**: “Put a broker between API and DB; accept quickly, process asynchronously, and batch DB writes.”
* **Caching**: “Cache status for hot IDs, but for high-cardinality polling prefer push (webhook) or conditional GETs.”
* **Batch writes**: “Buffer + bulk insert under idempotent keys to reduce write amplification.”
* **SAGA**: “Use SAGA or transactional outbox to keep distributed services eventually consistent with compensations.”
* **Kafka partitions**: “Consumers per group ≤ partitions; add partitions for parallelism.”
* **Spring JPA**: “Managed entities auto-flush at commit; detached entities need merge/save.”
* **DB migrations**: “Make schema changes backward-compatible and split deploy into expand → migrate data → contract.”

---

