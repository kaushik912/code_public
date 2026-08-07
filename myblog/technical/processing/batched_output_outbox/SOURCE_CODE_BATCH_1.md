# Source Code Batch

This file contains 5 source files.

---

## File: .mvn/wrapper/maven-wrapper.properties

```
wrapperVersion=3.3.4
distributionType=only-script
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.16/apache-maven-3.9.16-bin.zip
```

---

## File: HELP.md

```markdown
# Read Me First
The following was discovered as part of building this project:

* No Docker Compose services found. As of now, the application won't start! Please add at least one service to the `compose.yaml` file.

# Getting Started

### Reference Documentation
For further reference, please consider the following sections:

* [Official Apache Maven documentation](https://maven.apache.org/guides/index.html)
* [Spring Boot Maven Plugin Reference Guide](https://docs.spring.io/spring-boot/4.1.0/maven-plugin)
* [Create an OCI image](https://docs.spring.io/spring-boot/4.1.0/maven-plugin/build-image.html)
* [Spring Web](https://docs.spring.io/spring-boot/4.1.0/reference/web/servlet.html)
* [Spring Data JPA](https://docs.spring.io/spring-boot/4.1.0/reference/data/sql.html#data.sql.jpa-and-spring-data)
* [Spring for Apache Kafka](https://docs.spring.io/spring-boot/4.1.0/reference/messaging/kafka.html)
* [Docker Compose Support](https://docs.spring.io/spring-boot/4.1.0/reference/features/dev-services.html#features.dev-services.docker-compose)
* [Validation](https://docs.spring.io/spring-boot/4.1.0/reference/io/validation.html)

### Guides
The following guides illustrate how to use some features concretely:

* [Building a RESTful Web Service](https://spring.io/guides/gs/rest-service/)
* [Serving Web Content with Spring MVC](https://spring.io/guides/gs/serving-web-content/)
* [Building REST services with Spring](https://spring.io/guides/tutorials/rest/)
* [Accessing Data with JPA](https://spring.io/guides/gs/accessing-data-jpa/)
* [Validation](https://spring.io/guides/gs/validating-form-input/)

### Docker Compose support
This project contains a Docker Compose file named `compose.yaml`.

However, no services were found. As of now, the application won't start!

Please make sure to add at least one service in the `compose.yaml` file.

### Maven Parent overrides

Due to Maven's design, elements are inherited from the parent POM to the project POM.
While most of the inheritance is fine, it also inherits unwanted elements like `<license>` and `<developers>` from the parent.
To prevent this, the project POM contains empty overrides for these elements.
If you manually switch to a different parent and actually want the inheritance, you need to remove those overrides.

```

---

## File: README.md

```markdown
# Transactional Outbox Pattern — Spring Boot demo

A minimal, runnable example of the **transactional outbox** pattern.

`POST /register` writes a **user row** and an **outbox row** in the *same* DB
transaction. A scheduled **relay** later reads unprocessed outbox rows, publishes
them to **Kafka**, and marks them processed. A **consumer** subscribes to the
topic to prove the fan-out.

```
POST /register
      │  (ONE @Transactional)
      ▼
 ┌──────────┐      ┌───────────────┐
 │ app_user │      │ outbox_event  │   ← both commit together, or neither does
 └──────────┘      └───────┬───────┘
                           │  @Scheduled relay polls processed=false
                           ▼
                     KafkaTemplate ──► topic: user-events ──► @KafkaListener
```

## Why this pattern

You cannot atomically "save to the DB **and** publish to Kafka" — they are two
different systems with no shared transaction. Naively doing
`repo.save(); kafka.send();` gives you two failure windows:

- crash **after** DB commit, **before** send → event lost forever
- send **succeeds**, then DB tx **rolls back** → phantom event for a user that doesn't exist

The outbox removes the dual write: the app only ever writes to **one** system
(the DB). "User created" and "we owe Kafka a message" commit atomically. A
separate relay bridges DB → Kafka afterwards, retrying until Kafka acks.
Delivery is therefore **at-least-once**, so consumers should be idempotent.

## Run it

Requires Docker (for Kafka) and JDK 17+.

**Option A — start Kafka yourself, then run the jar:**

```bash
docker compose up -d          # starts single-node Kafka (KRaft) on localhost:9092
./mvnw -DskipTests package
java -jar target/outbox-demo-0.0.1-SNAPSHOT.jar
```

**Option B — let Spring auto-start Kafka:**

```bash
./mvnw spring-boot:run        # spring-boot-docker-compose reads compose.yaml and boots Kafka
```

Then, in another terminal:

```bash
curl -X POST http://localhost:8080/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com"}'
```

Within ~2s the app logs show the relay publishing and the consumer receiving:

```
[relay]    found 1 unprocessed outbox event(s)
[relay]    published outbox id=1 to user-events-0 @offset 0
[consumer] >>> received from Kafka: {"eventType":"UserRegistered","userId":1,...}
```

Verify the message is really in Kafka (independent of the app):

```bash
docker exec outbox-demo-kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic user-events --from-beginning --timeout-ms 4000
```

Stop everything: `Ctrl-C` the app, then `docker compose down`.

## Key files

| File | Role |
|---|---|
| `registration/RegistrationService.java` | The atomic write — user + outbox in one `@Transactional` |
| `outbox/OutboxEvent.java` | The outbox table |
| `outbox/OutboxRelay.java` | `@Scheduled` poller: outbox → Kafka, marks processed after broker ACK |
| `consumer/UserEventConsumer.java` | Downstream `@KafkaListener` (stand-in for another service) |
| `compose.yaml` | Single-node Kafka (KRaft, no ZooKeeper) |

## Notes for Spring Boot 4 (this project is on 4.1.0)

- **Jackson 3**: packages moved to `tools.jackson.*` (annotations stay
  `com.fasterxml.jackson.annotation`); its exceptions are now unchecked.
- **Starter names changed**: `spring-boot-starter-webmvc` (not `-web`),
  `spring-boot-starter-kafka`, `spring-boot-h2console`.
- `spring-boot-docker-compose` is **excluded from the packaged fat jar** (like
  devtools), so `java -jar` will *not* auto-start Kafka — use Option A above, or
  run via `./mvnw spring-boot:run` for auto-start.

## Production hardening (out of scope here, but know they exist)

- Relay polling adds latency and DB load. Alternatives: **Debezium / CDC**
  tailing the outbox table's transaction log (no polling, no processed flag).
- For multiple relay instances, guard the batch with
  `SELECT ... FOR UPDATE SKIP LOCKED` so two relays don't grab the same rows.
- Purge or archive processed rows periodically.
- Give each event a unique id (used here as the Kafka key domain) so consumers
  can dedupe under at-least-once delivery.
```

---

## File: compose.yaml

```yaml
services:
  kafka:
    image: 'apache/kafka:3.9.1'
    ports:
      - '9092:9092'
    environment:
      # --- single-node KRaft (no ZooKeeper): this node is both broker and controller ---
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@localhost:9093'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      # Listen for clients on 9092 and for the controller quorum on 9093
      KAFKA_LISTENERS: 'PLAINTEXT://:9092,CONTROLLER://:9093'
      # Tell clients (running on the host) how to reach the broker
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://localhost:9092'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT'
      # single-node: everything replicated once
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
```

---

## File: pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>4.1.0</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>
	<groupId>com.example</groupId>
	<artifactId>outbox-demo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>outbox-demo</name>
	<description/>
	<url/>
	<licenses>
		<license/>
	</licenses>
	<developers>
		<developer/>
	</developers>
	<scm>
		<connection/>
		<developerConnection/>
		<tag/>
		<url/>
	</scm>
	<properties>
		<java.version>17</java.version>
	</properties>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-h2console</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-kafka</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-validation</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-docker-compose</artifactId>
			<scope>runtime</scope>
			<optional>true</optional>
		</dependency>
		<dependency>
			<groupId>com.h2database</groupId>
			<artifactId>h2</artifactId>
			<scope>runtime</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-kafka-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-validation-test</artifactId>
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

