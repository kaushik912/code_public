# MySQL Transaction Concurrency Issue - Analysis & Solutions

## The Problem

MySQL's default isolation level is REPEATABLE READ, combined with a race condition:

- Transaction A (onGitRepoCreated) commits the state change to REGISTERING
- Transaction B (registerApp) starts and reads the app entity
- If Transaction B's snapshot was taken before Transaction A committed, it will see the old state (APP_INITIATED)
- This causes the log message: "Skip registerApp; appId=5 already state=APP_INITIATED"
- But when you query the database separately, you see state=REGISTERING because that transaction has already committed

---

## Solution Options & Tradeoffs

### ✅ Option 1: Restructure the Flow - Publish After Transaction Commits (IMPLEMENTED)

**What it does:**
- Uses `TransactionSynchronizationManager` to defer RabbitMQ publishing until after transaction commits
- Ensures state changes are visible before downstream commands are sent

**Pros:**
- ✅ Most reliable solution - eliminates the race condition completely
- ✅ No database configuration changes needed
- ✅ Works across all isolation levels
- ✅ Follows best practice: don't publish events until data is committed
- ✅ No performance impact
- ✅ Thread-safe and works with distributed systems

**Cons:**
- ❌ Requires code changes (but minimal and localized)
- ❌ Slightly more verbose code with the synchronization callback

**When to use:**
- **Best for:** Event-driven architectures where order and consistency matter
- This is the recommended approach for your use case

**Implementation complexity:** Low - just wrap publish calls in transaction callbacks

---

### Option 2: Change Transaction Isolation to READ_COMMITTED

**What it does:**
- Change MySQL isolation level from REPEATABLE READ to READ_COMMITTED
- Allows transactions to see the latest committed data

**Configuration:**
```yaml
spring:
  jpa:
    properties:
      hibernate:
        connection:
          isolation: 2  # READ_COMMITTED
```

**Pros:**
- ✅ Simple configuration change
- ✅ Can improve performance in high-concurrency scenarios (fewer locks)
- ✅ Reduces phantom read issues

**Cons:**
- ❌ **Non-repeatable reads:** Same query in a transaction can return different results
- ❌ **Lost updates risk:** Two transactions can overwrite each other's changes
- ❌ Application-wide impact - affects ALL queries/transactions
- ❌ Can break optimistic locking patterns
- ❌ May introduce subtle bugs in other parts of the application that rely on REPEATABLE READ

**When to use:**
- When you have simple read/write patterns
- When you don't need consistent reads within a transaction
- **Not recommended for this case** - too broad an impact for a specific race condition

**Implementation complexity:** Very low - just config change, but high risk

---

### Option 3: Use Pessimistic Locking

**What it does:**
- Lock the row when reading it (SELECT FOR UPDATE)
- Prevents other transactions from reading until the lock is released

**Implementation:**
```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT a FROM AppEntity a WHERE a.id = :id")
AppEntity findByIdWithLock(@Param("id") Long id);
```

**Pros:**
- ✅ Guarantees data consistency
- ✅ Prevents concurrent modifications
- ✅ Works well for high-contention scenarios

**Cons:**
- ❌ **Performance impact:** Locks block other transactions, reducing concurrency
- ❌ **Deadlock risk:** If multiple locks are acquired in different orders
- ❌ **Scalability issues:** Can create bottlenecks under high load
- ❌ Requires changes at the repository layer
- ❌ Overkill for this problem - you're not modifying the same row concurrently

**When to use:**
- Financial transactions where data integrity is critical
- When multiple services might update the same row simultaneously
- **Not ideal for this case** - you have sequential state changes, not concurrent updates

**Implementation complexity:** Medium - requires repository changes and careful deadlock management

---

### Option 4: Add a Small Delay Before Processing

**What it does:**
- Add `Thread.sleep()` or retry logic in the listener before reading state

**Implementation:**
```java
@RabbitListener(queues = RabbitConfig.Q_CMD_REGISTER_APP)
public void registerApp(Messages.RegisterAppCommand cmd) throws InterruptedException {
    Thread.sleep(100); // Wait for transaction to commit
    AppEntity app = appRepo.findById(cmd.appId()).orElseThrow();
    // ...
}
```

**Pros:**
- ✅ Simple to implement
- ✅ Minimal code changes

**Cons:**
- ❌ **Unreliable:** No guarantee the delay is sufficient
- ❌ **Performance impact:** Unnecessary delays slow down processing
- ❌ **Hacky workaround:** Doesn't address the root cause
- ❌ Still has race condition - just reduces the probability
- ❌ Harder to test and reason about
- ❌ May need tuning as system load changes

**When to use:**
- **Never** - this is a band-aid, not a solution
- Only acceptable as a temporary workaround during investigation

**Implementation complexity:** Very low - but it's a bad practice

---

## Comparison Matrix

| Solution | Reliability | Performance | Complexity | Scope | Risk |
|----------|-------------|-------------|------------|-------|------|
| **Publish After Commit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Localized | Low |
| READ_COMMITTED | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Application-wide | High |
| Pessimistic Locking | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Per-query | Medium |
| Delay/Retry | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Localized | Medium |

---

## Why "Publish After Commit" is Best for Your Case

1. **Event-driven architecture pattern:** You're using RabbitMQ for orchestration - events should only be published when data is committed
2. **No side effects:** Doesn't affect other parts of your application
3. **Testable:** Easy to verify that events are published in the correct order
4. **Standard practice:** This is how Spring's `@TransactionalEventListener` works internally
5. **Future-proof:** If you scale to multiple instances or add more state transitions, this pattern still works

---

## Alternative: Spring's @TransactionalEventListener

If you refactor to use Spring Events instead of direct RabbitMQ publishing, you can leverage built-in support:

```java
// Publisher
@Transactional
public void onGitRepoCreated(Messages.GitRepoCreatedEvent evt) {
    // ... state updates ...
    applicationEventPublisher.publishEvent(new RegisterAppEvent(appId, appName));
}

// Listener
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void handleRegisterAppEvent(RegisterAppEvent event) {
    rabbit.convertAndSend(RabbitConfig.CMD_EXCHANGE, "cmd.registerApp", cmd);
}
```

This achieves the same result with Spring-managed transaction synchronization.

---

## Summary

The implemented solution (Publish After Commit) is the right choice because it:
- Solves the root cause without side effects
- Follows event-driven architecture best practices
- Has minimal performance overhead
- Is maintainable and testable
- Works reliably in distributed systems
