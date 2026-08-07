# Source Code Batch

This file contains 3 source files.

---

## File: src/main/java/com/example/outbox/user/UserRepository.java

```java
package com.example.outbox.user;

import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<AppUser, Long> {
    boolean existsByUsername(String username);
}
```

---

## File: src/main/resources/application.properties

```
spring.application.name=outbox-demo

# --- Database (in-memory H2; console at http://localhost:8080/h2-console, jdbc:h2:mem:testdb) ---
spring.datasource.url=jdbc:h2:mem:testdb
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.h2.console.enabled=true

# --- Kafka ---
# spring-boot-docker-compose auto-discovers the broker from compose.yaml and sets
# bootstrap-servers for us; this line is just a fallback for running Kafka manually.
spring.kafka.bootstrap-servers=localhost:9092

spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.acks=all

spring.kafka.consumer.group-id=demo-consumer
spring.kafka.consumer.auto-offset-reset=earliest
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.apache.kafka.common.serialization.StringDeserializer

logging.level.com.example.outbox=INFO
```

---

## File: src/test/java/com/example/outbox/OutboxDemoApplicationTests.java

```java
package com.example.outbox;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class OutboxDemoApplicationTests {

	@Test
	void contextLoads() {
	}

}
```

---

