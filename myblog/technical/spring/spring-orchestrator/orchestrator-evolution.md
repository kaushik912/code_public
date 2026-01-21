# Evolving the Orchestrator: From Hardcoded to Configurable

## Current Limitations

Your current design hardcodes state transitions:
```java
// Hardcoded: specific methods for each transition
onGitRepoCreated() → transitions → publishes next command
onAppRegistered() → transitions → publishes next command
```

**Problems as workflow grows:**
- 10 steps = 10 handler methods
- 20 steps = 20 handler methods
- Every new step requires code changes
- Lots of repetitive boilerplate

---

## Solution 1: State Machine Configuration (Recommended)

### Define Workflow as Configuration

```java
package com.example.orchestrator.statemachine;

import com.example.orchestrator.domain.AppState;

public class WorkflowConfig {

  // Define the state machine as data
  public record StateTransition(
    AppState fromState,
    String onEvent,           // event that triggers this transition
    AppState toState,
    String nextCommand        // command to publish after transition (optional)
  ) {}

  public static final List<StateTransition> APP_WORKFLOW = List.of(
    // When APP_INITIATED receives gitRepoCreated event
    new StateTransition(
      AppState.APP_INITIATED,
      "evt.gitRepoCreated",
      AppState.GIT_REPO_CREATED,
      null  // intermediate state, no command yet
    ),

    // Then immediately transition to REGISTERING and publish command
    new StateTransition(
      AppState.GIT_REPO_CREATED,
      null,  // automatic transition
      AppState.REGISTERING,
      "cmd.registerApp"
    ),

    // When REGISTERING receives appRegistered event
    new StateTransition(
      AppState.REGISTERING,
      "evt.appRegistered",
      AppState.COMPLETED,
      null  // final state
    )

    // Add more steps easily:
    // new StateTransition(AppState.COMPLETED, "evt.deployed", AppState.DEPLOYED, "cmd.runTests"),
    // new StateTransition(AppState.DEPLOYED, "evt.testsCompleted", AppState.LIVE, null)
  );
}
```

### Generic Transition Handler

```java
package com.example.orchestrator.statemachine;

import com.example.orchestrator.domain.*;
import com.example.orchestrator.messaging.RabbitConfig;
import com.example.orchestrator.repo.AppRepo;
import com.example.orchestrator.repo.AppStateHistoryRepo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class StateMachineEngine {
  private static final Logger log = LoggerFactory.getLogger(StateMachineEngine.class);

  private final AppRepo appRepo;
  private final AppStateHistoryRepo historyRepo;
  private final RabbitTemplate rabbit;

  // Index transitions by (fromState, event) for fast lookup
  private final Map<String, WorkflowConfig.StateTransition> transitionMap;

  public StateMachineEngine(AppRepo appRepo, AppStateHistoryRepo historyRepo, RabbitTemplate rabbit) {
    this.appRepo = appRepo;
    this.historyRepo = historyRepo;
    this.rabbit = rabbit;

    // Build index
    this.transitionMap = WorkflowConfig.APP_WORKFLOW.stream()
      .collect(Collectors.toMap(
        t -> t.fromState() + ":" + (t.onEvent() != null ? t.onEvent() : "AUTO"),
        t -> t
      ));
  }

  /**
   * Generic event handler - replaces all the onXxxEvent methods
   */
  @Transactional
  public void handleEvent(String eventType, Long appId, String appName, String correlationId) {
    var app = appRepo.findById(appId).orElseThrow();

    // Find transition for current state + event
    String key = app.getState() + ":" + eventType;
    WorkflowConfig.StateTransition transition = transitionMap.get(key);

    if (transition == null) {
      log.warn("[corr={}] No transition found for state={}, event={}",
        correlationId, app.getState(), eventType);
      return;
    }

    // Idempotency: skip if already past this state
    if (isStateAfter(app.getState(), transition.toState())) {
      log.info("[corr={}] Ignoring {}; app already in state={}",
        correlationId, eventType, app.getState());
      return;
    }

    // Execute transition
    AppState fromState = app.getState();
    app.setState(transition.toState());
    appRepo.save(app);
    recordTransition(appId, fromState, transition.toState(), eventType, correlationId);

    log.info("[corr={}] Transition: appId={} {} -> {}",
      correlationId, appId, fromState, transition.toState());

    // Check for automatic transitions (no event trigger)
    processAutomaticTransitions(app, appName, correlationId);

    // Publish next command if configured
    if (transition.nextCommand() != null) {
      publishCommandAfterCommit(transition.nextCommand(), appId, appName, correlationId);
    }
  }

  /**
   * Process any automatic transitions (transitions with onEvent=null)
   */
  private void processAutomaticTransitions(AppEntity app, String appName, String correlationId) {
    String autoKey = app.getState() + ":AUTO";
    WorkflowConfig.StateTransition autoTransition = transitionMap.get(autoKey);

    while (autoTransition != null) {
      AppState fromState = app.getState();
      app.setState(autoTransition.toState());
      appRepo.save(app);
      recordTransition(app.getId(), fromState, autoTransition.toState(), "auto", correlationId);

      log.info("[corr={}] Auto-transition: appId={} {} -> {}",
        correlationId, app.getId(), fromState, autoTransition.toState());

      // Publish command if needed
      if (autoTransition.nextCommand() != null) {
        publishCommandAfterCommit(autoTransition.nextCommand(), app.getId(), appName, correlationId);
      }

      // Check for next automatic transition
      autoKey = app.getState() + ":AUTO";
      autoTransition = transitionMap.get(autoKey);
    }
  }

  private void publishCommandAfterCommit(String command, Long appId, String appName, String correlationId) {
    TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
      @Override
      public void afterCommit() {
        // Generic command - you'd need to adapt based on your message structure
        var payload = Map.of(
          "appId", appId,
          "appName", appName,
          "correlationId", correlationId
        );
        rabbit.convertAndSend(RabbitConfig.CMD_EXCHANGE, command, payload);
        log.info("[corr={}] Published {} for appId={} (after commit)", correlationId, command, appId);
      }
    });
  }

  private void recordTransition(Long appId, AppState from, AppState to, String reason, String correlationId) {
    var h = new AppStateHistoryEntity();
    h.setAppId(appId);
    h.setFromState(from);
    h.setToState(to);
    h.setReason(reason);
    h.setCorrelationId(correlationId);
    historyRepo.save(h);
  }

  private boolean isStateAfter(AppState current, AppState target) {
    // Simple ordinal comparison - assumes states are defined in order
    return current.ordinal() >= target.ordinal();
  }
}
```

### Simplified Orchestrator Event Listener

```java
package com.example.orchestrator.messaging;

import com.example.orchestrator.statemachine.StateMachineEngine;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class GenericOrchestratorListener {

  private final StateMachineEngine stateMachine;

  public GenericOrchestratorListener(StateMachineEngine stateMachine) {
    this.stateMachine = stateMachine;
  }

  @RabbitListener(queues = RabbitConfig.Q_EVT_GIT_CREATED)
  public void handleGitCreated(Messages.GitRepoCreatedEvent evt) {
    stateMachine.handleEvent("evt.gitRepoCreated", evt.appId(), evt.appName(), evt.correlationId());
  }

  @RabbitListener(queues = RabbitConfig.Q_EVT_APP_REGISTERED)
  public void handleAppRegistered(Messages.AppRegisteredEvent evt) {
    stateMachine.handleEvent("evt.appRegistered", evt.appId(), evt.appName(), evt.correlationId());
  }

  // Adding new event handlers is now trivial:
  // @RabbitListener(queues = RabbitConfig.Q_EVT_DEPLOYED)
  // public void handleDeployed(Messages.DeployedEvent evt) {
  //   stateMachine.handleEvent("evt.deployed", evt.appId(), evt.appName(), evt.correlationId());
  // }
}
```

---

## Solution 2: Add Failure Handling & Retries

### Extended State Enum

```java
package com.example.orchestrator.domain;

public enum AppState {
  APP_INITIATED,
  GIT_REPO_CREATED,
  REGISTERING,
  COMPLETED,

  // Failure states
  GIT_REPO_FAILED,
  REGISTRATION_FAILED,
  FAILED;

  public boolean isFailureState() {
    return this == GIT_REPO_FAILED || this == REGISTRATION_FAILED || this == FAILED;
  }
}
```

### Failure Tracking Entity

```java
package com.example.orchestrator.domain;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "app_failures")
public class AppFailureEntity {

  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private Long appId;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState failedAtState;

  @Column(nullable = false)
  private String errorMessage;

  @Column(nullable = false)
  private String correlationId;

  @Column(nullable = false)
  private Integer retryCount = 0;

  @Column(nullable = false)
  private Instant failedAt = Instant.now();

  // getters/setters
}
```

### Enhanced Workflow with Retries

```java
public class WorkflowConfig {

  public record StateTransition(
    AppState fromState,
    String onEvent,
    AppState toState,
    AppState failureState,    // NEW: where to go on failure
    String nextCommand,
    Integer maxRetries        // NEW: max retries for this step
  ) {
    // Convenience constructor for transitions without retries
    public StateTransition(AppState fromState, String onEvent, AppState toState, String nextCommand) {
      this(fromState, onEvent, toState, null, nextCommand, 0);
    }
  }

  public static final List<StateTransition> APP_WORKFLOW = List.of(
    new StateTransition(
      AppState.APP_INITIATED,
      "evt.gitRepoCreated",
      AppState.GIT_REPO_CREATED,
      AppState.GIT_REPO_FAILED,  // failure state
      null,
      3  // max 3 retries
    ),

    new StateTransition(
      AppState.GIT_REPO_CREATED,
      null,
      AppState.REGISTERING,
      null,
      "cmd.registerApp",
      0
    ),

    new StateTransition(
      AppState.REGISTERING,
      "evt.appRegistered",
      AppState.COMPLETED,
      AppState.REGISTRATION_FAILED,  // failure state
      null,
      3  // max 3 retries
    ),

    // Retry transitions - from failed state back to working state
    new StateTransition(
      AppState.GIT_REPO_FAILED,
      "cmd.retry",
      AppState.APP_INITIATED,  // restart this step
      null,
      "cmd.createGitRepo",
      0
    ),

    new StateTransition(
      AppState.REGISTRATION_FAILED,
      "cmd.retry",
      AppState.REGISTERING,  // restart this step
      null,
      "cmd.registerApp",
      0
    )
  );
}
```

### Failure Event Handling

```java
// Add to Messages.java
public record StepFailedEvent(Long appId, String appName, String step, String error, String correlationId) {}

// Add to StateMachineEngine
@Transactional
public void handleFailure(String failureEvent, Long appId, String appName,
                          String errorMessage, String correlationId) {
  var app = appRepo.findById(appId).orElseThrow();

  // Find transition to get failure state and max retries
  String key = app.getState() + ":" + failureEvent;
  WorkflowConfig.StateTransition transition = transitionMap.get(key);

  if (transition == null || transition.failureState() == null) {
    // No specific failure state, go to generic FAILED
    moveToState(app, AppState.FAILED, "error:" + failureEvent, correlationId);
    recordFailure(appId, app.getState(), errorMessage, correlationId, 0);
    return;
  }

  // Check retry count
  int retryCount = getRetryCount(appId, app.getState());

  if (retryCount < transition.maxRetries()) {
    // Still have retries - stay in current state and republish command
    log.warn("[corr={}] Step failed (retry {}/{}): appId={}, error={}",
      correlationId, retryCount + 1, transition.maxRetries(), appId, errorMessage);

    recordFailure(appId, app.getState(), errorMessage, correlationId, retryCount + 1);

    // Retry the command after delay (you'd use a scheduled retry mechanism in production)
    if (transition.nextCommand() != null) {
      publishCommandAfterCommit(transition.nextCommand(), appId, appName, correlationId);
    }
  } else {
    // Max retries exceeded - move to failure state
    log.error("[corr={}] Step failed permanently after {} retries: appId={}, error={}",
      correlationId, retryCount, appId, errorMessage);

    moveToState(app, transition.failureState(), "maxRetriesExceeded", correlationId);
    recordFailure(appId, app.getState(), errorMessage, correlationId, retryCount + 1);
  }
}

private void moveToState(AppEntity app, AppState toState, String reason, String correlationId) {
  AppState fromState = app.getState();
  app.setState(toState);
  appRepo.save(app);
  recordTransition(app.getId(), fromState, toState, reason, correlationId);
}

private void recordFailure(Long appId, AppState failedAtState, String errorMessage,
                          String correlationId, int retryCount) {
  var failure = new AppFailureEntity();
  failure.setAppId(appId);
  failure.setFailedAtState(failedAtState);
  failure.setErrorMessage(errorMessage);
  failure.setCorrelationId(correlationId);
  failure.setRetryCount(retryCount);
  failureRepo.save(failure);
}

private int getRetryCount(Long appId, AppState state) {
  return failureRepo.findLatestByAppIdAndState(appId, state)
    .map(AppFailureEntity::getRetryCount)
    .orElse(0);
}
```

---

## Solution 3: Database-Driven Workflow (Most Flexible)

For maximum flexibility, store the workflow in the database:

```java
@Entity
@Table(name = "workflow_transitions")
public class WorkflowTransitionEntity {

  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private String workflowType;  // e.g., "app-creation", "deployment"

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState fromState;

  @Column(nullable = false)
  private String onEvent;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState toState;

  @Column
  private String nextCommand;

  @Column
  private Integer maxRetries;

  @Column(nullable = false)
  private Integer sequenceOrder;  // for ordering transitions

  @Column(nullable = false)
  private Boolean active = true;  // enable/disable transitions without code change

  // getters/setters
}
```

**Benefits:**
- Change workflow without redeploying code
- A/B test different workflows
- Per-customer custom workflows
- Enable/disable steps dynamically

---

## Comparison: Which Approach to Use?

| Approach | Complexity | Flexibility | When to Use |
|----------|-----------|-------------|-------------|
| **Hardcoded** (current) | Low | Low | < 5 steps, rarely changes |
| **Config-based** (Solution 1) | Medium | Medium | 5-20 steps, occasional changes |
| **DB-driven** (Solution 3) | High | High | 20+ steps, frequent changes, multi-tenant |

---

## Next Steps

1. **Start with Solution 1** (State Machine Configuration)
   - Minimal refactoring from your current code
   - Handles most real-world scenarios
   - Easy to add new steps

2. **Add Solution 2** (Failure Handling)
   - Once you have Solution 1 working
   - Critical for production systems
   - Handles retries and error states

3. **Consider Solution 3** (DB-driven)
   - Only if you need runtime workflow changes
   - Useful for multi-tenant systems
   - Adds operational complexity

**Want me to help implement any of these solutions in your codebase?**
