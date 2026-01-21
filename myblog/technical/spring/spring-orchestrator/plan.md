Below is a **minimal but “real” Spring Boot orchestrator** using:

* **MySQL** for state (apps + step history)
* **RabbitMQ** for pub/sub (commands + events)
* **Spring Data JPA** for persistence
* **Spring AMQP** for messaging
* **Clear logging** for transitions + correlation ids
* **Idempotent-ish transitions** (won’t re-run a step if state already moved)

---

## Architecture (what runs where)

**API (Orchestrator app)**

* `POST /apps` → creates `App` row with `APP_INITIATED`
* publishes `CreateGitRepoCommand(appId, correlationId)` to RabbitMQ

**Worker (same Spring Boot app for simplicity)**

* listens `cmd.createGitRepo` → sleeps → updates DB → publishes `GitRepoCreatedEvent`
* orchestrator listens that event → publishes `RegisterAppCommand`
* worker listens `cmd.registerApp` → sleeps → updates DB → publishes `AppRegisteredEvent`
* orchestrator listens that event → moves state to `COMPLETED`

> You can later split “orchestrator” and “workers” into separate services; code stays nearly identical.

---

## 1) `docker-compose.yml`

```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: orchestrator
      MYSQL_USER: app
      MYSQL_PASSWORD: apppass
      MYSQL_ROOT_PASSWORD: rootpass
    ports:
      - "3306:3306"
    command: ["--default-authentication-plugin=mysql_native_password"]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 20

  rabbitmq:
    image: rabbitmq:3.13-management
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 5s
      timeout: 3s
      retries: 20
```

Run:

```bash
docker compose up -d
```

RabbitMQ UI: `http://localhost:15672` (guest/guest)

---

## 2) Spring Boot project (Maven)

### Quick Start with Spring Initializr

You can generate the starter project with this command:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,mysql,amqp \
  -d type=maven-project \
  -d language=java \
  -d name=simple-orchestrator \
  -d artifactId=simple-orchestrator \
  -d packageName=com.example.orchestrator \
  -d javaVersion=17 \
  -o simple-orchestrator.zip
```

Then unzip and add the validation dependency manually to `pom.xml`.

### `pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>4.0.1</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>
	<groupId>com.example</groupId>
	<artifactId>simple-orchestrator</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>simple-orchestrator</name>
	<description>Demo project for Spring Boot</description>
	<properties>
		<java.version>17</java.version>
	</properties>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-amqp</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-web</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-validation</artifactId>
		</dependency>
		<dependency>
			<groupId>com.fasterxml.jackson.core</groupId>
			<artifactId>jackson-databind</artifactId>
		</dependency>

		<dependency>
			<groupId>com.mysql</groupId>
			<artifactId>mysql-connector-j</artifactId>
			<scope>runtime</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-amqp-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
		</plugins>
	</build>

</project>
```

---

## 3) App config

### `src/main/resources/application.yml`

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/orchestrator?useSSL=false&allowPublicKeyRetrieval=true
    username: app
    password: apppass
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        format_sql: true

  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest

logging:
  level:
    com.example.orchestrator: INFO
    org.springframework.amqp: INFO
```

---

## 4) Domain model (MySQL state)

### `AppState.java`

```java
package com.example.orchestrator.domain;

public enum AppState {
  APP_INITIATED,
  GIT_REPO_CREATED,
  REGISTERING,
  COMPLETED,
  FAILED
}
```

### `AppEntity.java`

```java
package com.example.orchestrator.domain;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "apps", uniqueConstraints = @UniqueConstraint(name="uk_app_name", columnNames = "appName"))
public class AppEntity {

  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private String appName;

  @Column(nullable = false)
  private String createdBy;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState state;

  @Column(nullable = false)
  private Instant createdAt = Instant.now();

  @Column(nullable = false)
  private Instant updatedAt = Instant.now();

  @Version
  private Long version; // optimistic locking

  @PreUpdate
  void onUpdate() { this.updatedAt = Instant.now(); }

  // getters/setters omitted for brevity
  // (Generate with IDE)
}
```

### `AppStateHistoryEntity.java` (nice for learning transitions)

```java
package com.example.orchestrator.domain;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "app_state_history")
public class AppStateHistoryEntity {

  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private Long appId;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState fromState;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false)
  private AppState toState;

  @Column(nullable = false)
  private String reason;

  @Column(nullable = false)
  private String correlationId;

  @Column(nullable = false)
  private Instant at = Instant.now();

  // getters/setters
}
```

### Repos

```java
package com.example.orchestrator.repo;

import com.example.orchestrator.domain.AppEntity;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AppRepo extends JpaRepository<AppEntity, Long> {
  Optional<AppEntity> findByAppName(String appName);
}
```

```java
package com.example.orchestrator.repo;

import com.example.orchestrator.domain.AppStateHistoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AppStateHistoryRepo extends JpaRepository<AppStateHistoryEntity, Long> {}
```

---

## 5) Messaging setup (exchanges + queues)

We’ll do **one topic exchange for commands** and **one for events**.

### `RabbitConfig.java`

```java
package com.example.orchestrator.messaging;

import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

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
}
```

---

## 6) Message payloads (commands + events)

### `Messages.java`

```java
package com.example.orchestrator.messaging;

public class Messages {

  public record CreateGitRepoCommand(Long appId, String appName, String correlationId) {}
  public record RegisterAppCommand(Long appId, String appName, String correlationId) {}

  public record GitRepoCreatedEvent(Long appId, String appName, String correlationId) {}
  public record AppRegisteredEvent(Long appId, String appName, String correlationId) {}

  private Messages() {}
}
```

---

## 7) Orchestrator service (state transitions + publishing next step)

### `OrchestratorService.java`

```java
package com.example.orchestrator.service;

import com.example.orchestrator.domain.*;
import com.example.orchestrator.messaging.Messages;
import com.example.orchestrator.messaging.RabbitConfig;
import com.example.orchestrator.repo.AppRepo;
import com.example.orchestrator.repo.AppStateHistoryRepo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class OrchestratorService {
  private static final Logger log = LoggerFactory.getLogger(OrchestratorService.class);

  private final AppRepo appRepo;
  private final AppStateHistoryRepo historyRepo;
  private final RabbitTemplate rabbit;

  public OrchestratorService(AppRepo appRepo, AppStateHistoryRepo historyRepo, RabbitTemplate rabbit) {
    this.appRepo = appRepo;
    this.historyRepo = historyRepo;
    this.rabbit = rabbit;
  }

  @Transactional
  public AppEntity createApp(String appName, String createdBy) {
    String correlationId = UUID.randomUUID().toString();

    var app = new AppEntity();
    app.setAppName(appName);
    app.setCreatedBy(createdBy);
    app.setState(AppState.APP_INITIATED);

    app = appRepo.save(app);
    recordTransition(app.getId(), null, AppState.APP_INITIATED, "createApp", correlationId);

    log.info("[corr={}] App created: id={}, name={}, state={}", correlationId, app.getId(), appName, app.getState());

    // kick off step1
    var cmd = new Messages.CreateGitRepoCommand(app.getId(), app.getAppName(), correlationId);
    rabbit.convertAndSend(RabbitConfig.CMD_EXCHANGE, "cmd.createGitRepo", cmd);
    log.info("[corr={}] Published cmd.createGitRepo for appId={}", correlationId, app.getId());

    return app;
  }

  @Transactional
  public void onGitRepoCreated(Messages.GitRepoCreatedEvent evt) {
    var app = appRepo.findById(evt.appId()).orElseThrow();

    // idempotency guard
    if (app.getState() == AppState.GIT_REPO_CREATED || app.getState() == AppState.REGISTERING || app.getState() == AppState.COMPLETED) {
      log.info("[corr={}] Ignoring GitRepoCreated; app already in state={}", evt.correlationId(), app.getState());
      return;
    }

    var from = app.getState();
    app.setState(AppState.GIT_REPO_CREATED);
    appRepo.save(app);
    recordTransition(app.getId(), from, AppState.GIT_REPO_CREATED, "gitRepoCreated", evt.correlationId());

    log.info("[corr={}] Transition: appId={} {} -> {}", evt.correlationId(), app.getId(), from, app.getState());

    // move to step2
    from = app.getState();
    app.setState(AppState.REGISTERING);
    appRepo.save(app);
    recordTransition(app.getId(), from, AppState.REGISTERING, "startRegistering", evt.correlationId());
    log.info("[corr={}] Transition: appId={} {} -> {}", evt.correlationId(), app.getId(), from, app.getState());

    var cmd = new Messages.RegisterAppCommand(app.getId(), app.getAppName(), evt.correlationId());
    rabbit.convertAndSend(RabbitConfig.CMD_EXCHANGE, "cmd.registerApp", cmd);
    log.info("[corr={}] Published cmd.registerApp for appId={}", evt.correlationId(), app.getId());
  }

  @Transactional
  public void onAppRegistered(Messages.AppRegisteredEvent evt) {
    var app = appRepo.findById(evt.appId()).orElseThrow();

    if (app.getState() == AppState.COMPLETED) {
      log.info("[corr={}] Ignoring AppRegistered; already COMPLETED", evt.correlationId());
      return;
    }

    var from = app.getState();
    app.setState(AppState.COMPLETED);
    appRepo.save(app);
    recordTransition(app.getId(), from, AppState.COMPLETED, "appRegistered", evt.correlationId());

    log.info("[corr={}] Transition: appId={} {} -> {}", evt.correlationId(), app.getId(), from, app.getState());
  }

  private void recordTransition(Long appId, AppState from, AppState to, String reason, String correlationId) {
    var h = new AppStateHistoryEntity();
    h.setAppId(appId);
    h.setFromState(from == null ? to : from);
    h.setToState(to);
    h.setReason(reason);
    h.setCorrelationId(correlationId);
    historyRepo.save(h);
  }
}
```

---

## 8) Rabbit listeners (Orchestrator listens events, workers listen commands)

### Event listeners → orchestrator drives next step

```java
package com.example.orchestrator.messaging;

import com.example.orchestrator.service.OrchestratorService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class OrchestratorEventListener {

  private final OrchestratorService orchestrator;

  public OrchestratorEventListener(OrchestratorService orchestrator) {
    this.orchestrator = orchestrator;
  }

  @RabbitListener(queues = RabbitConfig.Q_EVT_GIT_CREATED)
  public void handleGitCreated(Messages.GitRepoCreatedEvent evt) {
    orchestrator.onGitRepoCreated(evt);
  }

  @RabbitListener(queues = RabbitConfig.Q_EVT_APP_REGISTERED)
  public void handleAppRegistered(Messages.AppRegisteredEvent evt) {
    orchestrator.onAppRegistered(evt);
  }
}
```

### Command listeners → “workers” do the step and publish completion events

```java
package com.example.orchestrator.messaging;

import com.example.orchestrator.domain.AppEntity;
import com.example.orchestrator.domain.AppState;
import com.example.orchestrator.repo.AppRepo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
public class WorkerCommandListener {
  private static final Logger log = LoggerFactory.getLogger(WorkerCommandListener.class);

  private final AppRepo appRepo;
  private final RabbitTemplate rabbit;

  public WorkerCommandListener(AppRepo appRepo, RabbitTemplate rabbit) {
    this.appRepo = appRepo;
    this.rabbit = rabbit;
  }

  @RabbitListener(queues = RabbitConfig.Q_CMD_CREATE_GIT)
  @Transactional
  public void createGitRepo(Messages.CreateGitRepoCommand cmd) throws InterruptedException {
    AppEntity app = appRepo.findById(cmd.appId()).orElseThrow();

    // guard: only run step1 when APP_INITIATED
    if (app.getState() != AppState.APP_INITIATED) {
      log.info("[corr={}] Skip createGitRepo; appId={} already state={}", cmd.correlationId(), cmd.appId(), app.getState());
      return;
    }

    log.info("[corr={}] Running createGitRepo (sleeping) for appId={}, name={}", cmd.correlationId(), cmd.appId(), cmd.appName());
    Thread.sleep(1500);

    // publish event
    var evt = new Messages.GitRepoCreatedEvent(cmd.appId(), cmd.appName(), cmd.correlationId());
    rabbit.convertAndSend(RabbitConfig.EVT_EXCHANGE, "evt.gitRepoCreated", evt);
    log.info("[corr={}] Published evt.gitRepoCreated for appId={}", cmd.correlationId(), cmd.appId());
  }

  @RabbitListener(queues = RabbitConfig.Q_CMD_REGISTER_APP)
  @Transactional
  public void registerApp(Messages.RegisterAppCommand cmd) throws InterruptedException {
    AppEntity app = appRepo.findById(cmd.appId()).orElseThrow();

    // guard: only run step2 when REGISTERING
    if (app.getState() != AppState.REGISTERING) {
      log.info("[corr={}] Skip registerApp; appId={} already state={}", cmd.correlationId(), cmd.appId(), app.getState());
      return;
    }

    log.info("[corr={}] Running registerApp (sleeping) for appId={}, name={}", cmd.correlationId(), cmd.appId(), cmd.appName());
    Thread.sleep(1500);

    var evt = new Messages.AppRegisteredEvent(cmd.appId(), cmd.appName(), cmd.correlationId());
    rabbit.convertAndSend(RabbitConfig.EVT_EXCHANGE, "evt.appRegistered", evt);
    log.info("[corr={}] Published evt.appRegistered for appId={}", cmd.correlationId(), cmd.appId());
  }
}
```

---

## 9) REST API

### `CreateAppRequest.java`

```java
package com.example.orchestrator.api;

import jakarta.validation.constraints.NotBlank;

public record CreateAppRequest(
  @NotBlank String appName,
  @NotBlank String createdBy
) {}
```

### `AppController.java`

```java
package com.example.orchestrator.api;

import com.example.orchestrator.domain.AppEntity;
import com.example.orchestrator.service.OrchestratorService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/apps")
public class AppController {

  private final OrchestratorService orchestrator;

  public AppController(OrchestratorService orchestrator) {
    this.orchestrator = orchestrator;
  }

  @PostMapping
  public ResponseEntity<AppEntity> create(@RequestBody @Valid CreateAppRequest req) {
    var app = orchestrator.createApp(req.appName(), req.createdBy());
    return ResponseEntity.ok(app);
  }
}
```

### `Application.java`

```java
package com.example.orchestrator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
```

---

## 10) Run it

1. Start infra:

```bash
docker compose up -d
```

2. Run Spring Boot:

```bash
mvn spring-boot:run
```

3. Create an app:

```bash
curl -X POST http://localhost:8080/apps \
  -H "Content-Type: application/json" \
  -d '{"appName":"sample","createdBy":"alice"}'
```

Watch logs; you should see:

* app created → `cmd.createGitRepo`
* worker runs step1 → `evt.gitRepoCreated`
* orchestrator transitions → publishes `cmd.registerApp`
* worker runs step2 → `evt.appRegistered`
* orchestrator transitions to `COMPLETED`

---

## 11) Troubleshooting

### Docker Compose Commands

Check the status of your containers:
```bash
docker compose ps
```

View MySQL logs:
```bash
docker compose logs -f mysql
```

View RabbitMQ logs:
```bash
docker compose logs -f rabbitmq
```

Connect to MySQL directly:
```bash
docker compose exec mysql mysql -uapp -papppass orchestrator
```

Once connected, you can run queries:
```sql
-- Check app states
SELECT id, appName, state, createdAt, updatedAt FROM apps;

-- Check state transition history
SELECT * FROM app_state_history ORDER BY at DESC LIMIT 20;

-- Find apps stuck in a particular state
SELECT id, appName, state FROM apps WHERE state = 'REGISTERING';
```

Restart services if needed:
```bash
docker compose restart mysql
docker compose restart rabbitmq
```

Stop and remove all containers:
```bash
docker compose down
```

Stop and remove all containers + volumes (clears database):
```bash
docker compose down -v
```

---

### Re-publishing Missed Messages

If a message gets lost or a command needs to be re-initiated, you can manually publish it through the RabbitMQ Management UI.

#### Option 1: Re-publish from RabbitMQ Management UI (quickest)

1. Open `http://localhost:15672` → **Exchanges**
2. Click your **commands exchange** (`orchestrator.commands`)
3. In **Publish message**:

* **Routing key**: `cmd.registerApp` (or whichever command you need to retry)
* **Properties → content_type**: `application/json`
* **Payload** (adjust appId, appName, and correlationId as needed):

**Example for appId=2:**

```json
{"appId":2,"appName":"sample","correlationId":"manual-retry-2-20260121"}
```

**Example for appId=5:**

```json
{"appId":5,"appName":"myapp","correlationId":"manual-retry-5-20260121"}
```

4. Click **Publish message**
5. Check logs to verify the command is processed

**Note:** Make sure the app state in the database matches what the command expects:
- `cmd.createGitRepo` expects state = `APP_INITIATED`
- `cmd.registerApp` expects state = `REGISTERING`

You can verify the current state with:
```sql
SELECT id, appName, state FROM apps WHERE id = <appId>;
```

---

