# Scaling Individual Message Handlers

## The Problem

**Scenario:**
- `cmd.createGitRepo` gets 1000 messages/min (needs 10 workers)
- `cmd.registerApp` gets 10 messages/min (needs 1 worker)
- `cmd.deployApp` gets 100 messages/min (needs 5 workers)

**Question:** How do you scale each handler independently?

---

## Solution 1: Separate Queues (Easy Scaling)

### Each queue can have independent concurrency settings

```java
@Component
public class WorkerCommandListener {

  // createGitRepo: high load → 10 concurrent consumers
  @RabbitListener(
    queues = RabbitConfig.Q_CMD_CREATE_GIT,
    concurrency = "5-10"  // min 5, max 10 concurrent consumers
  )
  public void createGitRepo(Messages.CreateGitRepoCommand cmd) {
    log.info("[Worker-{}] Processing createGitRepo for appId={}",
      Thread.currentThread().getName(), cmd.appId());
    // slow operation
    Thread.sleep(5000);
  }

  // registerApp: low load → 1-2 concurrent consumers
  @RabbitListener(
    queues = RabbitConfig.Q_CMD_REGISTER_APP,
    concurrency = "1-2"  // min 1, max 2 concurrent consumers
  )
  public void registerApp(Messages.RegisterAppCommand cmd) {
    log.info("[Worker-{}] Processing registerApp for appId={}",
      Thread.currentThread().getName(), cmd.appId());
    // medium operation
    Thread.sleep(2000);
  }

  // deployApp: medium load → 5 concurrent consumers
  @RabbitListener(
    queues = RabbitConfig.Q_CMD_DEPLOY_APP,
    concurrency = "3-5"  // min 3, max 5 concurrent consumers
  )
  public void deployApp(Messages.DeployAppCommand cmd) {
    log.info("[Worker-{}] Processing deployApp for appId={}",
      Thread.currentThread().getName(), cmd.appId());
    // fast operation
    Thread.sleep(1000);
  }
}
```

### How it works

```
q.cmd.createGitRepo (1000 msg/min)
  ├─ Consumer Thread 1 [processing]
  ├─ Consumer Thread 2 [processing]
  ├─ Consumer Thread 3 [processing]
  ├─ Consumer Thread 4 [processing]
  ├─ Consumer Thread 5 [processing]
  ├─ Consumer Thread 6 [processing]
  ├─ Consumer Thread 7 [processing]
  ├─ Consumer Thread 8 [processing]
  ├─ Consumer Thread 9 [processing]
  └─ Consumer Thread 10 [processing]

q.cmd.registerApp (10 msg/min)
  └─ Consumer Thread 11 [idle most of the time]

q.cmd.deployApp (100 msg/min)
  ├─ Consumer Thread 12 [processing]
  ├─ Consumer Thread 13 [processing]
  ├─ Consumer Thread 14 [processing]
  ├─ Consumer Thread 15 [processing]
  └─ Consumer Thread 16 [processing]
```

**Total threads: 16 (10 + 1 + 5)**

### Dynamic Scaling with Configuration

```yaml
# application.yml
rabbitmq:
  listeners:
    create-git-repo:
      concurrency: 5-10
      max-concurrency: 20  # can burst to 20 during spikes
    register-app:
      concurrency: 1-2
      max-concurrency: 3
    deploy-app:
      concurrency: 3-5
      max-concurrency: 10
```

```java
@RabbitListener(
  queues = RabbitConfig.Q_CMD_CREATE_GIT,
  concurrency = "${rabbitmq.listeners.create-git-repo.concurrency}"
)
public void createGitRepo(Messages.CreateGitRepoCommand cmd) {
  // handler code
}
```

**Change concurrency without code changes** - just update config and restart.

---

## Solution 2: Shared Queue (Difficult Scaling)

### Problem: All handlers share the same consumer pool

```java
@Component
public class WorkerCommandListener {

  // Single listener with fixed concurrency for ALL commands
  @RabbitListener(
    queues = RabbitConfig.Q_ALL_COMMANDS,
    concurrency = "1-10"  // applies to ALL command types
  )
  public void handleCommand(Message message) {
    String routingKey = message.getMessageProperties().getReceivedRoutingKey();

    switch (routingKey) {
      case "cmd.createGitRepo" -> createGitRepo(...);  // slow, 5s
      case "cmd.registerApp" -> registerApp(...);      // medium, 2s
      case "cmd.deployApp" -> deployApp(...);          // fast, 1s
    }
  }
}
```

### The Scaling Problem

```
q.commands (1110 messages total)
  ├─ Thread 1: [createGitRepo - 5s] ← blocked
  ├─ Thread 2: [createGitRepo - 5s] ← blocked
  ├─ Thread 3: [createGitRepo - 5s] ← blocked
  ├─ Thread 4: [createGitRepo - 5s] ← blocked
  ├─ Thread 5: [createGitRepo - 5s] ← blocked
  ├─ Thread 6: [createGitRepo - 5s] ← blocked
  ├─ Thread 7: [createGitRepo - 5s] ← blocked
  ├─ Thread 8: [createGitRepo - 5s] ← blocked
  ├─ Thread 9: [createGitRepo - 5s] ← blocked
  └─ Thread 10: [createGitRepo - 5s] ← blocked

  registerApp messages waiting... 😢
  deployApp messages waiting... 😢
```

**Problem:** Slow `createGitRepo` messages monopolize all consumer threads. Fast `deployApp` messages get starved even though they could be processed quickly.

---

## Solution 3: Workarounds for Shared Queue Scaling

### Option A: Manual Message Routing with Async Executors

```java
@Component
public class WorkerCommandListener {

  // Separate thread pools for each command type
  private final ExecutorService gitRepoExecutor = Executors.newFixedThreadPool(10);
  private final ExecutorService registerExecutor = Executors.newFixedThreadPool(2);
  private final ExecutorService deployExecutor = Executors.newFixedThreadPool(5);

  @RabbitListener(
    queues = RabbitConfig.Q_ALL_COMMANDS,
    concurrency = "1-20"  // high concurrency for routing
  )
  public void handleCommand(Message message) {
    String routingKey = message.getMessageProperties().getReceivedRoutingKey();

    // Quickly route to appropriate executor - don't block the listener thread
    switch (routingKey) {
      case "cmd.createGitRepo" -> {
        var cmd = parseMessage(message, Messages.CreateGitRepoCommand.class);
        gitRepoExecutor.submit(() -> createGitRepo(cmd));  // async
      }
      case "cmd.registerApp" -> {
        var cmd = parseMessage(message, Messages.RegisterAppCommand.class);
        registerExecutor.submit(() -> registerApp(cmd));  // async
      }
      case "cmd.deployApp" -> {
        var cmd = parseMessage(message, Messages.DeployAppCommand.class);
        deployExecutor.submit(() -> deployApp(cmd));  // async
      }
    }
    // Listener thread returns immediately, actual work happens in executor
  }

  @Transactional
  private void createGitRepo(Messages.CreateGitRepoCommand cmd) {
    // 10 threads from gitRepoExecutor can run this
    log.info("[GitRepo-{}] Processing", Thread.currentThread().getName());
    Thread.sleep(5000);
  }

  @Transactional
  private void registerApp(Messages.RegisterAppCommand cmd) {
    // 2 threads from registerExecutor can run this
    log.info("[Register-{}] Processing", Thread.currentThread().getName());
    Thread.sleep(2000);
  }

  @Transactional
  private void deployApp(Messages.DeployAppCommand cmd) {
    // 5 threads from deployExecutor can run this
    log.info("[Deploy-{}] Processing", Thread.currentThread().getName());
    Thread.sleep(1000);
  }
}
```

### How it works

```
q.commands
  │
  ├─ Listener Thread 1 [routes msg] → returns immediately
  ├─ Listener Thread 2 [routes msg] → returns immediately
  ├─ ... (20 listener threads total, all fast)
  └─ Listener Thread 20 [routes msg] → returns immediately
       │
       ├──→ gitRepoExecutor (10 threads)
       │     ├─ Thread 1 [createGitRepo - 5s]
       │     ├─ Thread 2 [createGitRepo - 5s]
       │     └─ ...
       │
       ├──→ registerExecutor (2 threads)
       │     └─ Thread 1 [registerApp - 2s]
       │
       └──→ deployExecutor (5 threads)
             ├─ Thread 1 [deployApp - 1s]
             └─ ...
```

**Pros:**
- ✅ Independent scaling per message type
- ✅ Fast messages don't wait for slow messages
- ✅ Keep shared queue simplicity

**Cons:**
- ❌ Manual executor management
- ❌ More complex error handling
- ❌ Need to handle executor shutdown
- ❌ RabbitMQ acknowledgements become tricky (must ack after executor completes)
- ❌ Lose Spring's @Transactional integration (harder to manage)

### Option B: Priority Queues (Doesn't solve scaling, just ordering)

```java
@Bean
Queue commandQueue() {
  return QueueBuilder.durable(Q_ALL_COMMANDS)
    .withArgument("x-max-priority", 10)  // enable priorities
    .build();
}

// Publishing with priority
rabbit.convertAndSend(CMD_EXCHANGE, "cmd.deployApp", cmd, message -> {
  message.getMessageProperties().setPriority(10);  // high priority
  return message;
});

rabbit.convertAndSend(CMD_EXCHANGE, "cmd.createGitRepo", cmd, message -> {
  message.getMessageProperties().setPriority(1);  // low priority
  return message;
});
```

**This doesn't help with scaling** - just changes which messages get processed first. You still have the same number of consumers.

### Option C: Split Into Separate Queues Selectively

```java
// Keep MOST commands in shared queue
@Bean
Binding bindMostCommands(Queue commandQueue, TopicExchange commandsExchange) {
  return BindingBuilder.bind(commandQueue).to(commandsExchange).with("cmd.*");
}

// But give createGitRepo its own queue since it's high volume
@Bean
Queue gitRepoQueue() { return QueueBuilder.durable("q.cmd.createGitRepo").build(); }

@Bean
Binding bindGitRepoCommand(Queue gitRepoQueue, TopicExchange commandsExchange) {
  return BindingBuilder.bind(gitRepoQueue).to(commandsExchange).with("cmd.createGitRepo");
}

// Separate listeners
@RabbitListener(queues = "q.cmd.createGitRepo", concurrency = "5-10")
public void createGitRepo(Messages.CreateGitRepoCommand cmd) {
  // dedicated scaling for high-volume command
}

@RabbitListener(queues = RabbitConfig.Q_ALL_COMMANDS, concurrency = "1-3")
public void handleOtherCommands(Message message) {
  switch (routingKey) {
    case "cmd.registerApp" -> registerApp(...);
    case "cmd.deployApp" -> deployApp(...);
    // createGitRepo NOT here - has its own queue
  }
}
```

**This is the pragmatic hybrid approach.**

---

## Solution 4: Horizontal Scaling (Multiple Application Instances)

### Instead of more threads, run more app instances

```bash
# Instance 1
RABBITMQ_CONCURRENCY=5 java -jar orchestrator.jar

# Instance 2
RABBITMQ_CONCURRENCY=5 java -jar orchestrator.jar

# Instance 3
RABBITMQ_CONCURRENCY=5 java -jar orchestrator.jar
```

```
q.cmd.createGitRepo
  │
  ├─ Instance 1 (5 consumers) ─┐
  ├─ Instance 2 (5 consumers) ─┼─ 15 total consumers
  └─ Instance 3 (5 consumers) ─┘
```

**With separate queues:**
```java
// Each instance has these concurrency settings
@RabbitListener(queues = "q.cmd.createGitRepo", concurrency = "10")
@RabbitListener(queues = "q.cmd.registerApp", concurrency = "2")
@RabbitListener(queues = "q.cmd.deployApp", concurrency = "5")

// Scale up instances during createGitRepo spike
// - createGitRepo gets 10 consumers × N instances
// - registerApp gets 2 consumers × N instances
// - deployApp gets 5 consumers × N instances
```

**With shared queue:**
```java
@RabbitListener(queues = "q.commands", concurrency = "10")

// Scale up instances during createGitRepo spike
// - All command types share 10 consumers × N instances
// - createGitRepo still monopolizes most consumers
// - Other commands still starved
```

**Separate queues scale better horizontally** because each queue maintains its consumer ratio.

---

## Real-World Example: GitHub API Rate Limiting

### Scenario
```
cmd.createGitRepo:
  - Calls GitHub API (rate limited: 1 request/second)
  - High volume: 1000 requests waiting
  - Need: Many workers, but each waits 1s between calls

cmd.deployApp:
  - Calls internal API (no rate limit)
  - Medium volume: 100 requests waiting
  - Need: Few workers, but very fast processing
```

### With Separate Queues

```java
// Many workers, but each processes slowly (rate limited)
@RabbitListener(
  queues = "q.cmd.createGitRepo",
  concurrency = "20"  // 20 workers @ 1 req/sec = 20 req/sec throughput
)
public void createGitRepo(Messages.CreateGitRepoCommand cmd) {
  callGitHubAPI();
  Thread.sleep(1000);  // rate limit wait
}

// Few workers, but each processes quickly
@RabbitListener(
  queues = "q.cmd.deployApp",
  concurrency = "3"  // 3 workers @ 100 req/sec = fast
)
public void deployApp(Messages.DeployAppCommand cmd) {
  callInternalAPI();
  // no wait, returns immediately
}
```

**Result:**
- createGitRepo: 20 req/sec throughput (20 workers × 1 req/sec each)
- deployApp: processes all 100 messages in ~1 second

### With Shared Queue

```java
@RabbitListener(queues = "q.commands", concurrency = "20")
public void handleCommand(Message message) {
  switch (routingKey) {
    case "cmd.createGitRepo" -> {
      callGitHubAPI();
      Thread.sleep(1000);  // blocks this thread for 1 second
    }
    case "cmd.deployApp" -> {
      callInternalAPI();
      // returns immediately, but had to wait for available thread
    }
  }
}
```

**Result:**
- All 20 threads get filled with createGitRepo (because there are 1000 waiting)
- deployApp messages wait in queue even though they could be processed instantly
- createGitRepo: still 20 req/sec throughput
- deployApp: processes slowly, 1 message per second (when a thread becomes free)

---

## Monitoring & Dynamic Scaling

### With Separate Queues: Easy to Monitor

```
Queue Name              Messages Ready    Consumers    Msg/sec
q.cmd.createGitRepo     850               10           20
q.cmd.registerApp       0                 1            0.2
q.cmd.deployApp         15                5            10
```

**Action:** Increase createGitRepo consumers from 10 → 20

### With Shared Queue: Hard to Monitor

```
Queue Name         Messages Ready    Consumers    Msg/sec
q.commands         865               15           30
```

**Problem:** You can't see which message type is causing the backlog without inspecting individual messages.

---

## Performance Comparison

### Spike Scenario: createGitRepo gets 10x traffic

| Metric | Separate Queues | Shared Queue | Shared Queue + Executors |
|--------|----------------|--------------|--------------------------|
| **createGitRepo latency** | Low (can scale) | High (limited consumers) | Medium (executor pool) |
| **deployApp latency** | Low (independent) | **High (starved!)** | Medium (has dedicated pool) |
| **Configuration complexity** | Medium | Low | High |
| **Monitoring clarity** | High | Low | Medium |
| **Scale independently?** | ✅ Yes | ❌ No | ✅ Yes (with code) |
| **Simple code?** | ✅ Yes | ✅ Yes | ❌ No |

---

## Recommendation

### Use Separate Queues When:

1. **Different message types have different throughput requirements**
   - High volume vs low volume
   - Example: 1000 createGitRepo/min vs 10 registerApp/min

2. **Different message types have different processing times**
   - Slow vs fast operations
   - Example: 5s GitHub API call vs 100ms database update

3. **Different message types have different external dependencies**
   - Rate limited APIs vs unlimited internal APIs
   - Example: GitHub API (rate limited) vs internal DB (fast)

4. **You need independent horizontal scaling**
   - Scale createGitRepo workers without scaling registerApp workers

### Use Shared Queues When:

1. **All message types have similar throughput**
   - All ~100 messages/min

2. **All message types have similar processing time**
   - All ~1 second operations

3. **You want simpler configuration**
   - Fewer queues to manage

4. **You're okay with "good enough" scaling**
   - Scale all handlers together

---

## Migration Path: Start Shared, Split When Needed

### Step 1: Start with Shared Queue
```java
@RabbitListener(queues = "q.commands", concurrency = "1-5")
public void handleCommand(Message message) {
  switch (routingKey) {
    case "cmd.createGitRepo" -> createGitRepo(...);
    case "cmd.registerApp" -> registerApp(...);
    case "cmd.deployApp" -> deployApp(...);
  }
}
```

### Step 2: Monitor Production Metrics
```
Observation: createGitRepo takes 80% of processing time
Action: Move it to separate queue
```

### Step 3: Split High-Volume Handler
```java
// createGitRepo gets its own queue
@RabbitListener(queues = "q.cmd.createGitRepo", concurrency = "10-20")
public void createGitRepo(Messages.CreateGitRepoCommand cmd) { }

// Others stay in shared queue
@RabbitListener(queues = "q.commands", concurrency = "1-3")
public void handleCommand(Message message) {
  switch (routingKey) {
    case "cmd.registerApp" -> registerApp(...);
    case "cmd.deployApp" -> deployApp(...);
  }
}
```

### Step 4: Split More as Needed
Repeat for any other high-volume or slow handlers.

---

## Summary

**The key insight:** Separate queues give you a dedicated "lane" for each message type. Shared queues put all messages in the same lane.

```
Separate Queues = Multiple Lanes
┌──────────────┐
│ createGit    │ ═══════════════ (10 cars, slow)
├──────────────┤
│ registerApp  │ ═ (1 car, medium)
├──────────────┤
│ deployApp    │ ═════ (5 cars, fast)
└──────────────┘

Shared Queue = Single Lane
┌──────────────────────────────┐
│ All commands                 │ ══════════════════ (createGit blocks everyone)
└──────────────────────────────┘
```

**For your orchestrator with createGitRepo spikes:** Use separate queues or the hybrid approach to prevent slow commands from blocking fast ones.
