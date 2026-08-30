Here is how I would stack it for backend engineers who are learning in 2026. 

### Junior backend developer

1. Layered backend (API / service / DB)
    - Handlers on top, business logic in the middle, data access at the bottom.

2. Monolithic service + single relational DB
    - One deployable, one database, use transactions to keep writes safe.

3. CRUD flows and transaction boundaries
    - Create, read, update, delete with clear start and end of a transaction.

4. Simple cache aside pattern
    - Read from cache, fall back to DB, write to cache when data changes.

### Mid level backend developer

1. Modular monolith
    - One deployable, but clear modules around each domain.

2. REST API design and versioning
    - Clean resource names, correct status codes, v1 vs v2 contracts.

3. Background workers and job queues
    - Move slow work off the request path, handle retries and dead letters.

4. Event driven integration (pub / sub)
    - Services publish events, other services subscribe and react.

5. API gateway in front of services
    - Single entry point for routing, auth, rate limits, logging.

6. Read replicas for scaling
    - Primary for writes, replicas for hot read endpoints, accept some lag.

### Senior backend engineer

1. Evolution path: monolith → modular → services
    - Split only when teams and domains are ready, not because of hype.

2. Saga pattern for multi service workflows
    - Orchestrate steps with compensating actions instead of one big transaction.

3. CQRS only where complexity demands it
    - Separate write model and read model for heavy domains, keep others simple.

4. Sharding and multi region data
    - Partition by tenant or key, plan for hot shards and rebalancing.

5. Rate limiting, throttling, back pressure
    - Protect databases and services when traffic spikes.

6. Strangler fig and anti corruption layers
    - Wrap legacy systems, replace them slice by slice without blowing things up.

7. Sidecars and service mesh for cross cutting concerns
    - Put TLS, retries, metrics near the service, not inside every handler.

In the beginning, patterns help you build.
Later, they help you choose what not to build.