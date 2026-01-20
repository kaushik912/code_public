# Older systems were monolithic
- A large, self-contained application
- Complex
- Tightly coupled

# SOA
- reusable software components called services
- each service should execute a discrete business function
- typically at enterprise level

# Microservices
- One of the most difficult parts of architecting a new service application is designing the service boundaries.
- Microservices running on one platform can connect to microservices on another platform
- Each microservice can be scaled independently
- Infra and cost can be optimized based on traffic requirements

- More services means more deployments => more points of failure.
- More operational skill is required
- Operations team must manages ten,hundreds or thousands of microservices
- "spider-web" of communication between microservices
- Increased communication latency 
- integration testing is more challenging
- Debugging is also challenging
- If an application consists of many microservices and each microservice creates it own logs, tracing calls that span many microservices can be challenging

- So its fine to start with a monolith if the team doesn't understand the problem domain and gradually move to microservices.

# Event Driven Architecture
- Event is record of something that happened.
- Immutable fact (historical record)
- Event can be generated even if its never consumed
- Event can be persisted indefinitely and consumed as many times as necessary
- Point to Point communication introduces tight coupling between the services
- An event driven architecture introduces "event-intermediary" between the services

## Benefits of Event driven apps
- Provides Auditing
- Event can provide a timed, ordered record of every change to the state of the application


# Service Choreography
- Service choreography similar to dance choreography
- when a dance is choreographed, dancers are instructed how to perform the dance but dancers are fully responsible for performing their parts during the dance
- A distributed application is harder to understand because there's no central source of truth.

# Service Orchestation
- Similar to Orchestra performance
- Each musician in the orchestra knows how to play their instrument but conductor takes an active role during the performance to ensure musicians are synchronized.
- Orchestration provides a high-level view of business processes which helps with understanding the application, tracking exeuction and troubleshooting issues.
- Unlike Service Choreography, Service orchestration has a single point of failure.
- If orchestrator is not operable, the orchestrated processes cannot run.

## Google Pub/Sub
- Pub/Sub is one of the services in google cloud to choreograph services.
- Events are delivered to targets using the standard `CNCF` CloudEvent format, regardless of event source.

## Google Workflow
- Google Cloud's `workflow` platform to implement the orchestration platform.
- You can use Google's eventarc to send events between the services.

- Most systems do a mix of Orchestration and Choreography.
    - For core payment, we can use orchestration
        - eg: 
            1. fraud checks
            2. payment gateway
            3. order service
            4. ledger service
    - For side-effects, we can use choreography.
        - eg: email, analytics, loyalty points 
### Saga Pattern
- Saga is a distributed transaction pattern that replaces rollback with compensation

```
BEGIN TRANSACTION
    createOrder()
    chargePayment()
    reserveInventory()
END
```
- Here createOrder could be a separate microservice and talking to its DB.
- Similarly chargePayment and reserveInventory could be different microservices.

- So, what if step 3 fails but Step1 and Step2 succeeded?
- in Saga, you compensate.

- So, here createOrder -> chargePayment -> reserveInventory
- In case reserveInventory fails, you `compensate`
    - RefundPayment
    - CancelOrder

# Benefits
 - Central Control
 - Clear State Machine
 - Easier to reason about.
 - Eventual Consistency

# What is eventual consistency?
- User performs an action
    - Transaction DB is updated
    - Analytics dashboard updates later ( say batch job)
    - Reports lag by minutes or hours
- User places an order and immediately checks profile page
    - Orders page: shows order
    - Shipping page: not yet visible
    - Email confirmation: arrives later
    - Points:
        - No transaction failed
        - No compensation needed
        - Still "eventually" consistent.
        

# Google Cloud Tasks
- A reliable execution mechanism used by the orchestrator.
- It handles delivery, retries, applies rate limits, guarantees atleast once delivert.
- Its a managed task queue often used by orchestrator to reliably execute workflow steps

# Orchestrator points 
- Typically, orchestrator doesn't wait in `memory`. It waits via `state`
- Eg: 
- Command -> Event -> State Transition
    - Step1: Orchestrator send command (via queue/say cloud tasks)
        - enqueue: authorize_payment
        - task queue delivers request to service A
        - orchestrator immediately returns, goes IDLE
        - State is NOW: PAYMENT_AUTH_IN_PROGRESS
    - Step2: Service A finishes 
        - emits an event PaymentAuthorized
        - or calls back an endpoint (/payment/result)
        - or updates a shared record
        - This is a **signal**, not a return value
    - Step3: Orchestrator reacts to the signal
        - receives the event or callback
        - validates it (idempotency!)
        - updates state, STATE is AUTHORIZED
    - Then, enqueue: capture_payment
- This makes it non-blocking.
- To make it crash-safe, it should store like:
    - current step
    - step results
    - timestamps
    - retry count

- Its not like, Orchestrator is doing:  
    - call Service A
    - wait 30s
    - call Service B
    - wait 30s
- The above approach makes it robust and non-blocking.

### One-liners!
- `Orchestrator`: sends commands, tracks state
- `Services`: do work, emit fact( events)
- `Event bus`: routes facts to whoever cares.
