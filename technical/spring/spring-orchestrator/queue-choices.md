# RabbitMQ Queue Design Choices

## The Question

**Do we need a separate queue for each command and event?**

Current setup creates many queues:
```
cmd.createGitRepo → q.cmd.createGitRepo
cmd.registerApp → q.cmd.registerApp
evt.gitRepoCreated → q.evt.gitRepoCreated
evt.appRegistered → q.evt.appRegistered
```

Adding a new step = 2 new queues (1 command + 1 event)

---

## Option 1: One Queue Per Message Type (Current Design)

### Configuration

```java
@Configuration
public class RabbitConfig {

  public static final String CMD_EXCHANGE = "orchestrator.commands";
  public static final String EVT_EXCHANGE = "orchestrator.events";

  public static final String Q_CMD_CREATE_GIT = "q.cmd.createGitRepo";
  public static final String Q_CMD_REGISTER_APP = "q.cmd.registerApp";
  public static final String Q_EVT_GIT_CREATED = "q.evt.gitRepoCreated";
  public static final String Q_EVT_APP_REGISTERED = "q.evt.appRegistered";

  @Bean
  TopicExchange commandsExchange() { return new TopicExchange(CMD_EXCHANGE); }

  @Bean
  TopicExchange eventsExchange() { return new TopicExchange(EVT_EXCHANGE); }

  @Bean Queue qCmdCreateGitRepo() { return QueueBuilder.durable(Q_CMD_CREATE_GIT).build(); }
  @Bean Queue qCmdRegisterApp() { return QueueBuilder.durable(Q_CMD_REGISTER_APP).build(); }
  @Bean Queue qEvtGitCreated() { return QueueBuilder.durable(Q_EVT_GIT_CREATED).build(); }
  @Bean Queue qEvtAppRegistered() { return QueueBuilder.durable(Q_EVT_APP_REGISTERED).build(); }

  @Bean
  Binding bindCmdCreateGit(Queue qCmdCreateGitRepo, TopicExchange commandsExchange) {
    return BindingBuilder.bind(qCmdCreateGitRepo).to(commandsExchange).with("cmd.createGitRepo");
  }

  @Bean
  Binding bindCmdRegisterApp(Queue qCmdRegisterApp, TopicExchange commandsExchange) {
    return BindingBuilder.bind(qCmdRegisterApp).to(commandsExchange).with("cmd.registerApp");
  }

  @Bean
  Binding bindEvtGitCreated(Queue qEvtGitCreated, TopicExchange eventsExchange) {
    return BindingBuilder.bind(qEvtGitCreated).to(eventsExchange).with("evt.gitRepoCreated");
  }

  @Bean
  Binding bindEvtAppRegistered(Queue qEvtAppRegistered, TopicExchange eventsExchange) {
    return BindingBuilder.bind(qEvtAppRegistered).to(eventsExchange).with("evt.appRegistered");
  }

  @Bean
  public MessageConverter messageConverter() {
    return new Jackson2JsonMessageConverter();
  }
}
```

### Listeners

```java
@Component
public class WorkerCommandListener {

  @RabbitListener(queues = RabbitConfig.Q_CMD_CREATE_GIT)
  public void createGitRepo(Messages.CreateGitRepoCommand cmd) {
    // handle command
  }

  @RabbitListener(queues = RabbitConfig.Q_CMD_REGISTER_APP)
  public void registerApp(Messages.RegisterAppCommand cmd) {
    // handle command
  }

  // Adding new command = new @RabbitListener method + new queue + new binding
}
```

### Pros
- ✅ Each queue has specific purpose
- ✅ Easy to see message flow in RabbitMQ UI
- ✅ Can apply different policies per queue (TTL, DLQ, priority)
- ✅ Can scale consumers differently per message type
- ✅ Type-safe message deserialization (Spring does it automatically)

### Cons
- ❌ Lots of boilerplate (queue + binding per message type)
- ❌ Adding new message type requires config changes
- ❌ Many queues to monitor and manage

### When to Use
- Different microservices consume different messages
- Need different scaling per message type
- Need different error handling or retry policies
- Need different TTL or priority settings

---

## Option 2: Shared Queues (Recommended for Monolith)

### Configuration

```java
@Configuration
public class RabbitConfig {

  public static final String CMD_EXCHANGE = "orchestrator.commands";
  public static final String EVT_EXCHANGE = "orchestrator.events";

  // Just TWO queues total!
  public static final String Q_ALL_COMMANDS = "q.commands";
  public static final String Q_ALL_EVENTS = "q.events";

  @Bean
  TopicExchange commandsExchange() { return new TopicExchange(CMD_EXCHANGE); }

  @Bean
  TopicExchange eventsExchange() { return new TopicExchange(EVT_EXCHANGE); }

  @Bean
  Queue commandQueue() { return QueueBuilder.durable(Q_ALL_COMMANDS).build(); }

  @Bean
  Queue eventQueue() { return QueueBuilder.durable(Q_ALL_EVENTS).build(); }

  // Route ALL commands to the same queue
  @Bean
  Binding bindAllCommands(Queue commandQueue, TopicExchange commandsExchange) {
    return BindingBuilder.bind(commandQueue).to(commandsExchange).with("cmd.#");
    // "cmd.#" is a wildcard: matches cmd.createGitRepo, cmd.registerApp, cmd.anything
  }

  // Route ALL events to the same queue
  @Bean
  Binding bindAllEvents(Queue eventQueue, TopicExchange eventsExchange) {
    return BindingBuilder.bind(eventQueue).to(eventsExchange).with("evt.#");
    // "evt.#" is a wildcard: matches evt.gitRepoCreated, evt.appRegistered, evt.anything
  }

  @Bean
  public MessageConverter messageConverter() {
    return new Jackson2JsonMessageConverter();
  }
}
```

### Listeners (Routing by Message Type)

```java
@Component
public class WorkerCommandListener {
  private static final Logger log = LoggerFactory.getLogger(WorkerCommandListener.class);

  private final AppRepo appRepo;
  private final RabbitTemplate rabbit;
  private final Jackson2JsonMessageConverter converter = new Jackson2JsonMessageConverter();

  public WorkerCommandListener(AppRepo appRepo, RabbitTemplate rabbit) {
    this.appRepo = appRepo;
    this.rabbit = rabbit;
  }

  // Single listener for ALL commands
  @RabbitListener(queues = RabbitConfig.Q_ALL_COMMANDS)
  public void handleCommand(Message message) throws Exception {
    String routingKey = message.getMessageProperties().getReceivedRoutingKey();

    log.info("Received command: {}", routingKey);

    switch (routingKey) {
      case "cmd.createGitRepo" -> {
        var cmd = parseMessage(message, Messages.CreateGitRepoCommand.class);
        createGitRepo(cmd);
      }
      case "cmd.registerApp" -> {
        var cmd = parseMessage(message, Messages.RegisterAppCommand.class);
        registerApp(cmd);
      }
      case "cmd.deployApp" -> {
        var cmd = parseMessage(message, Messages.DeployAppCommand.class);
        deployApp(cmd);
      }
      // Add new commands here - no queue config changes needed!
      default -> log.warn("Unknown command: {}", routingKey);
    }
  }

  @Transactional
  private void createGitRepo(Messages.CreateGitRepoCommand cmd) throws InterruptedException {
    AppEntity app = appRepo.findById(cmd.appId()).orElseThrow();

    if (app.getState() != AppState.APP_INITIATED) {
      log.info("[corr={}] Skip createGitRepo; appId={} already state={}",
        cmd.correlationId(), cmd.appId(), app.getState());
      return;
    }

    log.info("[corr={}] Running createGitRepo for appId={}, name={}",
      cmd.correlationId(), cmd.appId(), cmd.appName());
    Thread.sleep(1500);

    var evt = new Messages.GitRepoCreatedEvent(cmd.appId(), cmd.appName(), cmd.correlationId());
    rabbit.convertAndSend(RabbitConfig.EVT_EXCHANGE, "evt.gitRepoCreated", evt);
    log.info("[corr={}] Published evt.gitRepoCreated for appId={}", cmd.correlationId(), cmd.appId());
  }

  @Transactional
  private void registerApp(Messages.RegisterAppCommand cmd) throws InterruptedException {
    AppEntity app = appRepo.findById(cmd.appId()).orElseThrow();

    if (app.getState() != AppState.REGISTERING) {
      log.info("[corr={}] Skip registerApp; appId={} already state={}",
        cmd.correlationId(), cmd.appId(), app.getState());
      return;
    }

    log.info("[corr={}] Running registerApp for appId={}, name={}",
      cmd.correlationId(), cmd.appId(), cmd.appName());
    Thread.sleep(1500);

    var evt = new Messages.AppRegisteredEvent(cmd.appId(), cmd.appName(), cmd.correlationId());
    rabbit.convertAndSend(RabbitConfig.EVT_EXCHANGE, "evt.appRegistered", evt);
    log.info("[corr={}] Published evt.appRegistered for appId={}", cmd.correlationId(), cmd.appId());
  }

  @Transactional
  private void deployApp(Messages.DeployAppCommand cmd) throws InterruptedException {
    // New command handler - no queue changes needed!
    log.info("[corr={}] Running deployApp for appId={}", cmd.correlationId(), cmd.appId());
    Thread.sleep(2000);

    var evt = new Messages.AppDeployedEvent(cmd.appId(), cmd.appName(), cmd.correlationId());
    rabbit.convertAndSend(RabbitConfig.EVT_EXCHANGE, "evt.appDeployed", evt);
    log.info("[corr={}] Published evt.appDeployed for appId={}", cmd.correlationId(), cmd.appId());
  }

  private <T> T parseMessage(Message message, Class<T> type) {
    return (T) converter.fromMessage(message, type);
  }
}
```

```java
@Component
public class OrchestratorEventListener {

  private final OrchestratorService orchestrator;
  private final Jackson2JsonMessageConverter converter = new Jackson2JsonMessageConverter();

  public OrchestratorEventListener(OrchestratorService orchestrator) {
    this.orchestrator = orchestrator;
  }

  // Single listener for ALL events
  @RabbitListener(queues = RabbitConfig.Q_ALL_EVENTS)
  public void handleEvent(Message message) {
    String routingKey = message.getMessageProperties().getReceivedRoutingKey();

    log.info("Received event: {}", routingKey);

    switch (routingKey) {
      case "evt.gitRepoCreated" -> {
        var evt = parseMessage(message, Messages.GitRepoCreatedEvent.class);
        orchestrator.onGitRepoCreated(evt);
      }
      case "evt.appRegistered" -> {
        var evt = parseMessage(message, Messages.AppRegisteredEvent.class);
        orchestrator.onAppRegistered(evt);
      }
      case "evt.appDeployed" -> {
        var evt = parseMessage(message, Messages.AppDeployedEvent.class);
        orchestrator.onAppDeployed(evt);
      }
      // Add new events here - no queue config changes needed!
      default -> log.warn("Unknown event: {}", routingKey);
    }
  }

  private <T> T parseMessage(Message message, Class<T> type) {
    return (T) converter.fromMessage(message, type);
  }
}
```

### Pros
- ✅ Minimal queue configuration (just 2 queues)
- ✅ Adding new message = just add case in switch
- ✅ Less boilerplate
- ✅ Easier to manage (fewer queues)
- ✅ Same consumer app handles all messages of same type

### Cons
- ❌ Manual message deserialization (routing key → message type mapping)
- ❌ Can't scale individual message handlers independently
- ❌ Can't apply different policies per message type
- ❌ Larger switch statement as workflow grows

### When to Use
- Single application (monolith) handles all messages
- All messages have similar priority/policies
- All messages should be processed with same scaling
- Workflow changes frequently (easier to add new messages)

---

## Option 3: Hybrid Approach

### Group related messages into shared queues

```java
// Commands grouped by worker type
public static final String Q_GIT_COMMANDS = "q.git.commands";
public static final String Q_DEPLOYMENT_COMMANDS = "q.deployment.commands";
public static final String Q_REGISTRATION_COMMANDS = "q.registration.commands";

// Events grouped by domain
public static final String Q_GIT_EVENTS = "q.git.events";
public static final String Q_DEPLOYMENT_EVENTS = "q.deployment.events";

@Bean
Binding bindGitCommands(Queue qGitCommands, TopicExchange commandsExchange) {
  return BindingBuilder.bind(qGitCommands).to(commandsExchange).with("cmd.git.#");
  // Matches: cmd.git.create, cmd.git.delete, cmd.git.update
}

@Bean
Binding bindDeploymentCommands(Queue qDeploymentCommands, TopicExchange commandsExchange) {
  return BindingBuilder.bind(qDeploymentCommands).to(commandsExchange).with("cmd.deploy.#");
  // Matches: cmd.deploy.start, cmd.deploy.rollback, cmd.deploy.verify
}
```

### Pros
- ✅ Balance between granularity and simplicity
- ✅ Can scale different domains independently
- ✅ Can apply different policies per domain
- ✅ Less boilerplate than one-queue-per-message

### Cons
- ❌ Need to decide on grouping strategy
- ❌ Still some manual routing logic

### When to Use
- Different teams own different domains
- Different scaling needs per domain
- Want some policy flexibility without too many queues

---

## Option 4: Single Queue for Everything

```java
@Bean
Queue everythingQueue() { return QueueBuilder.durable("q.everything").build(); }

@Bean
Binding bindEverything(Queue everythingQueue, TopicExchange exchange) {
  return BindingBuilder.bind(everythingQueue).to(exchange).with("#");
}

@RabbitListener(queues = "q.everything")
public void handleMessage(Message message) {
  String routingKey = message.getMessageProperties().getReceivedRoutingKey();

  if (routingKey.startsWith("cmd.")) {
    handleCommand(routingKey, message);
  } else if (routingKey.startsWith("evt.")) {
    handleEvent(routingKey, message);
  }
}
```

### Pros
- ✅ Simplest possible setup
- ✅ Zero queue management overhead

### Cons
- ❌ No separation of concerns
- ❌ Can't scale commands vs events separately
- ❌ Harder to debug and monitor
- ❌ All messages compete for same consumer threads

### When to Use
- Prototyping or very simple workflows
- Single consumer handles everything
- Not recommended for production

---

## When Do You NEED Separate Queues?

### 1. Different Consumers (Microservices)
```
q.cmd.createGitRepo → GitWorkerService
q.cmd.registerApp → RegistrationService
q.cmd.deployApp → DeploymentService
```
Each service only listens to its own queue.

### 2. Different Scaling Requirements
```
q.cmd.createGitRepo → 1 worker (slow, sequential, rate-limited by GitHub API)
q.cmd.processPayment → 10 workers (fast, can parallelize)
q.cmd.sendEmail → 5 workers (medium speed)
```

### 3. Different Priorities
```
q.cmd.highPriority → x-max-priority: 10
q.cmd.normalPriority → x-max-priority: 5
q.cmd.lowPriority → x-max-priority: 1
```

### 4. Different Error Handling Policies
```
q.cmd.critical →
  - x-message-ttl: infinite
  - x-dead-letter-exchange: dlx.critical
  - max retries: 10

q.cmd.optional →
  - x-message-ttl: 3600000 (1 hour)
  - x-dead-letter-exchange: dlx.optional
  - max retries: 1
```

### 5. Different Message TTL
```
q.cmd.urgent → x-message-ttl: 300000 (5 minutes)
q.cmd.batch → x-message-ttl: 86400000 (24 hours)
```

### 6. Different Visibility Requirements
```
q.cmd.internal → only internal services can access
q.evt.public → external subscribers can listen
```

---

## Comparison Table

| Approach | # Queues | Config Complexity | Runtime Flexibility | Independent Scaling | Best For |
|----------|----------|-------------------|---------------------|---------------------|----------|
| **One per message** | Many (2n for n steps) | High | Low | Yes | Microservices, different policies |
| **Shared queues** | Few (2-3) | Low | High | No | Monolith, uniform policies |
| **Hybrid** | Medium (5-10) | Medium | Medium | Partial | Domain-driven design |
| **Single queue** | 1 | Very Low | Very High | No | Prototypes only |

---

## Recommendation for Your Orchestrator

### Current State: Monolith Application

**Use Option 2: Shared Queues**

```
✓ q.commands → All worker commands (WorkerCommandListener)
✓ q.events → All orchestrator events (OrchestratorEventListener)
```

**Reasons:**
1. Your workers are in the **same application**, not separate microservices
2. All commands have **similar priority and policies**
3. **Much simpler** - adding new commands = just add a case in switch
4. **Easier to manage** - 2 queues vs 20+ queues
5. You can always refactor later if needed

### Future: When to Switch to Separate Queues

**Move to Option 1 (separate queues) when:**
- You split workers into separate microservices
- Different commands need different scaling (1 worker vs 10 workers)
- Different commands need different retry policies
- Different commands have different SLAs

### Migration Path

Going from shared → separate queues is easy:

1. Create new specific queue
2. Add binding for specific routing key
3. Remove that case from switch statement
4. Add dedicated @RabbitListener

The messages and exchange structure stays the same!

---

## Example Migration

### Before (Shared)
```java
@RabbitListener(queues = "q.commands")
public void handleCommand(Message message) {
  switch (routingKey) {
    case "cmd.createGitRepo" -> createGitRepo(...);
    case "cmd.processPayment" -> processPayment(...);
  }
}
```

### After (Mixed)
```java
// Payment needs its own queue for scaling
@RabbitListener(queues = "q.cmd.processPayment", concurrency = "5-10")
public void processPayment(Messages.ProcessPaymentCommand cmd) {
  // dedicated handler with 5-10 concurrent consumers
}

// Other commands still shared
@RabbitListener(queues = "q.commands")
public void handleCommand(Message message) {
  switch (routingKey) {
    case "cmd.createGitRepo" -> createGitRepo(...);
    // payment removed - has its own queue now
  }
}
```

---

## Summary

**Key Insight:** Queues are for **distribution**, not **routing**.

- **Routing** happens via routing keys (`cmd.createGitRepo`)
- **Distribution** happens via queues (who processes it, how, and with what policies)

If everyone in your team sits in the same application with the same policies, you don't need separate queues. The routing keys already tell you what message it is.

**Start simple (shared queues), split when you have a specific reason.**
