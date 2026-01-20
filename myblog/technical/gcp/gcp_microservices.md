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

- Pub/Sub is one of the services in google cloud to choreograph services.
- Events are delivered to targets using the standard `CNCF` CloudEvent format, regardless of event source.

- Google Cloud's workflow platform to implement the orchestration platform.
