# Orchestrator System Design Diagram

## Architecture Overview

```mermaid
graph TB
    subgraph ClientLayer["Client"]
        HTTPClient[HTTP Client]
    end

    subgraph SpringApp["Spring Boot Application"]
        subgraph APILayer["API Layer"]
            Controller[AppController<br/>POST /apps]
        end

        subgraph OrchestratorLayer["Orchestrator Layer"]
            OrchestratorService[OrchestratorService<br/>- createApp<br/>- onGitRepoCreated<br/>- onAppRegistered]
            OrchestratorEventListener[OrchestratorEventListener<br/>Listens to Events]
        end

        subgraph WorkerLayer["Worker Layer"]
            WorkerCommandListener[WorkerCommandListener<br/>Listens to Commands]
        end

        subgraph DataLayer["Data Layer"]
            AppRepo[AppRepo]
            HistoryRepo[AppStateHistoryRepo]
        end
    end

    subgraph Infra["Infrastructure"]
        MySQL[(MySQL Database<br/>- apps table<br/>- app_state_history)]

        subgraph RabbitMQ["RabbitMQ"]
            CmdExchange[Commands Exchange<br/>orchestrator.commands]
            EvtExchange[Events Exchange<br/>orchestrator.events]

            Q1[Queue: cmd.createGitRepo]
            Q2[Queue: cmd.registerApp]
            Q3[Queue: evt.gitRepoCreated]
            Q4[Queue: evt.appRegistered]
        end
    end

    HTTPClient -->|POST| Controller
    Controller --> OrchestratorService
    OrchestratorService --> AppRepo
    OrchestratorService --> HistoryRepo
    AppRepo --> MySQL
    HistoryRepo --> MySQL

    OrchestratorService -.->|Publish Command| CmdExchange
    CmdExchange --> Q1
    CmdExchange --> Q2

    Q1 --> WorkerCommandListener
    Q2 --> WorkerCommandListener

    WorkerCommandListener -.->|Publish Event| EvtExchange
    EvtExchange --> Q3
    EvtExchange --> Q4

    Q3 --> OrchestratorEventListener
    Q4 --> OrchestratorEventListener
    OrchestratorEventListener --> OrchestratorService

    style HTTPClient fill:#e1f5ff
    style Controller fill:#fff4e1
    style OrchestratorService fill:#ffe1f5
    style WorkerCommandListener fill:#e1ffe1
    style MySQL fill:#ffe1e1
    style CmdExchange fill:#f0e1ff
    style EvtExchange fill:#e1fff0
```

## Sequence Diagram - Complete Flow

```mermaid
sequenceDiagram
    actor User
    participant API as AppController
    participant Orch as OrchestratorService
    participant DB as MySQL
    participant CmdEx as Commands Exchange
    participant Worker as WorkerCommandListener
    participant EvtEx as Events Exchange
    participant EvtListen as OrchestratorEventListener

    User->>API: POST /apps {appName, createdBy}

    rect rgb(255, 244, 225)
        Note over API,DB: Step 1: Create App
        API->>Orch: createApp(appName, createdBy)
        Orch->>DB: INSERT app (state=APP_INITIATED)
        Orch->>DB: INSERT history (APP_INITIATED)
        Orch-->>CmdEx: Publish cmd.createGitRepo
        Note over Orch,CmdEx: Published AFTER transaction commits
        Orch->>API: Return AppEntity
    end
    API->>User: 200 OK {id, appName, state}

    rect rgb(225, 255, 225)
        Note over CmdEx,EvtEx: Step 2: Create Git Repo
        CmdEx->>Worker: cmd.createGitRepo
        Worker->>DB: SELECT app (verify state=APP_INITIATED)
        Worker->>Worker: Simulate work (sleep 1500ms)
        Worker-->>EvtEx: Publish evt.gitRepoCreated
    end

    rect rgb(255, 225, 245)
        Note over EvtEx,DB: Step 3: Transition to REGISTERING
        EvtEx->>EvtListen: evt.gitRepoCreated
        EvtListen->>Orch: onGitRepoCreated(event)
        Orch->>DB: UPDATE app (state=GIT_REPO_CREATED)
        Orch->>DB: INSERT history (GIT_REPO_CREATED)
        Orch->>DB: UPDATE app (state=REGISTERING)
        Orch->>DB: INSERT history (REGISTERING)
        Orch-->>CmdEx: Publish cmd.registerApp
        Note over Orch,CmdEx: Published AFTER transaction commits
    end

    rect rgb(225, 255, 225)
        Note over CmdEx,EvtEx: Step 4: Register App
        CmdEx->>Worker: cmd.registerApp
        Worker->>DB: SELECT app (verify state=REGISTERING)
        Worker->>Worker: Simulate work (sleep 1500ms)
        Worker-->>EvtEx: Publish evt.appRegistered
    end

    rect rgb(255, 225, 245)
        Note over EvtEx,DB: Step 5: Complete
        EvtEx->>EvtListen: evt.appRegistered
        EvtListen->>Orch: onAppRegistered(event)
        Orch->>DB: UPDATE app (state=COMPLETED)
        Orch->>DB: INSERT history (COMPLETED)
    end
```

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> APP_INITIATED: POST /apps

    APP_INITIATED --> GIT_REPO_CREATED: evt.gitRepoCreated<br/>(worker completes)

    GIT_REPO_CREATED --> REGISTERING: Immediate transition<br/>(orchestrator)

    REGISTERING --> COMPLETED: evt.appRegistered<br/>(worker completes)

    APP_INITIATED --> FAILED: Error
    GIT_REPO_CREATED --> FAILED: Error
    REGISTERING --> FAILED: Error

    COMPLETED --> [*]
    FAILED --> [*]

    note right of APP_INITIATED
        cmd.createGitRepo published
        Worker starts git repo creation
    end note

    note right of REGISTERING
        cmd.registerApp published
        Worker starts app registration
    end note

    note right of COMPLETED
        Workflow complete
        No further actions
    end note
```

## Component Interaction Map

```mermaid
graph LR
    subgraph "Message Flow Pattern"
        A[Orchestrator Service] -->|1. Publishes COMMAND| B[RabbitMQ Commands]
        B -->|2. Routes to| C[Worker Listener]
        C -->|3. Does Work| D[Worker Logic]
        D -->|4. Publishes EVENT| E[RabbitMQ Events]
        E -->|5. Routes to| F[Orchestrator Event Listener]
        F -->|6. Triggers| A
    end

    style A fill:#ffe1f5
    style C fill:#e1ffe1
    style D fill:#e1ffe1
    style F fill:#fff4e1
    style B fill:#f0e1ff
    style E fill:#e1fff0
```

## Data Model

```mermaid
erDiagram
    APPS ||--o{ APP_STATE_HISTORY : has

    APPS {
        bigint id PK
        varchar appName UK
        varchar createdBy
        enum state
        timestamp createdAt
        timestamp updatedAt
        bigint version
    }

    APP_STATE_HISTORY {
        bigint id PK
        bigint appId FK
        enum fromState
        enum toState
        varchar reason
        varchar correlationId
        timestamp at
    }
```

## Key Design Decisions

### 1. Event-Driven Architecture
- **Pattern**: Command/Event Segregation
- **Commands**: Imperative actions for workers (cmd.createGitRepo, cmd.registerApp)
- **Events**: State change notifications (evt.gitRepoCreated, evt.appRegistered)
- **Benefit**: Loose coupling between orchestrator and workers

### 2. Transaction Safety
- **Problem**: Race condition between DB commit and message consumption
- **Solution**: Publish commands AFTER transaction commits using `TransactionSynchronizationManager`
- **Result**: Workers always see committed state when processing commands

### 3. Idempotency Guards
- **Workers**: Check expected state before processing (prevents duplicate work)
- **Orchestrator**: Ignores events if already in later state (handles retries)

### 4. Correlation IDs
- **Purpose**: Track request flow across async boundaries
- **Usage**: Every command/event carries correlationId for debugging
- **Benefit**: Easy to trace entire workflow in logs

### 5. State History
- **Table**: app_state_history tracks all transitions
- **Value**: Audit trail, debugging, analytics
- **Pattern**: Event Sourcing lite

## Scalability Considerations

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB[Load Balancer]

        subgraph "Orchestrator Instances"
            O1[Orchestrator 1]
            O2[Orchestrator 2]
            O3[Orchestrator N...]
        end

        subgraph "Worker Instances"
            W1[Worker 1]
            W2[Worker 2]
            W3[Worker N...]
        end

        LB --> O1
        LB --> O2
        LB --> O3

        O1 & O2 & O3 -.-> RMQ[RabbitMQ Cluster]
        RMQ -.-> W1
        RMQ -.-> W2
        RMQ -.-> W3

        O1 & O2 & O3 --> DB[(MySQL Primary)]
        W1 & W2 & W3 --> DB

        DB -.->|Replication| DB2[(MySQL Replica)]
    end

    style O1 fill:#ffe1f5
    style O2 fill:#ffe1f5
    style O3 fill:#ffe1f5
    style W1 fill:#e1ffe1
    style W2 fill:#e1ffe1
    style W3 fill:#e1ffe1
```

### Scale-out Strategy:
1. **API Layer**: Stateless - scale horizontally behind load balancer
2. **Orchestrator**: Stateless - multiple instances can process events concurrently
3. **Workers**: Stateless - RabbitMQ distributes work across instances (competing consumers)
4. **Database**: Single writer with read replicas for queries
5. **RabbitMQ**: Cluster for high availability

## Message Guarantee Levels

| Component | Guarantee | How |
|-----------|-----------|-----|
| **Database** | Exactly-once state change | ACID transactions + optimistic locking |
| **RabbitMQ** | At-least-once delivery | Durable queues + publisher confirms |
| **Worker Idempotency** | Safe retry | State guards prevent duplicate work |
| **Overall System** | Eventual consistency | Idempotent handlers + correlation tracking |

---

## How to View These Diagrams

These diagrams use Mermaid syntax. View them using:

1. **GitHub/GitLab**: Renders automatically in markdown files
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **IntelliJ IDEA**: Built-in Mermaid support in markdown preview
4. **Online**: Paste into https://mermaid.live
5. **CLI**: Use `mmdc` (mermaid-cli) to generate PNG/SVG

Example to generate PNG:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i system-design-diagram.md -o architecture.png
```
