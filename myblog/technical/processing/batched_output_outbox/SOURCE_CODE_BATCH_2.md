# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/outbox/OutboxDemoApplication.java

```java
package com.example.outbox;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling // enables the @Scheduled outbox relay poller
public class OutboxDemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(OutboxDemoApplication.class, args);
	}

}
```

---

## File: src/main/java/com/example/outbox/config/KafkaTopicConfig.java

```java
package com.example.outbox.config;

import com.example.outbox.outbox.OutboxRelay;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaTopicConfig {

    /** Auto-created on startup by KafkaAdmin. */
    @Bean
    public NewTopic userEventsTopic() {
        return TopicBuilder.name(OutboxRelay.TOPIC)
                .partitions(1)
                .replicas(1)
                .build();
    }
}
```

---

## File: src/main/java/com/example/outbox/consumer/UserEventConsumer.java

```java
package com.example.outbox.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * A downstream subscriber. In real life this would live in another service
 * (email, analytics, search indexer, ...). Here it just logs, to prove the
 * message fanned out through Kafka after the outbox relay published it.
 */
@Component
public class UserEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(UserEventConsumer.class);

    @KafkaListener(topics = "user-events", groupId = "demo-consumer")
    public void onUserEvent(String message) {
        log.info("[consumer] >>> received from Kafka: {}", message);
    }
}
```

---

## File: src/main/java/com/example/outbox/outbox/OutboxEvent.java

```java
package com.example.outbox.outbox;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

import java.time.Instant;

/**
 * One row per domain event that needs to reach Kafka.
 *
 * It is written IN THE SAME DB TRANSACTION as the business change (the user row).
 * A separate relay later reads unprocessed rows and publishes them to Kafka.
 * That is the whole outbox pattern: the DB is the single source of truth, so the
 * "did the business change happen" and "did we record intent to publish" facts
 * commit atomically — no lost or phantom messages from a mid-flight crash.
 */
@Entity
@Table(name = "outbox_event",
        indexes = @Index(name = "idx_outbox_unprocessed", columnList = "processed, id"))
public class OutboxEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** e.g. "user" — the kind of aggregate this event is about. */
    @Column(nullable = false)
    private String aggregateType;

    /** e.g. the user id — used as the Kafka message key so a given user's events stay ordered. */
    @Column(nullable = false)
    private String aggregateId;

    /** e.g. "UserRegistered". */
    @Column(nullable = false)
    private String eventType;

    /** JSON payload published as the Kafka message value. */
    @Lob
    @Column(nullable = false)
    private String payload;

    @Column(nullable = false)
    private Instant createdAt;

    /** false = still needs publishing; flipped to true once Kafka has acked it. */
    @Column(nullable = false)
    private boolean processed;

    private Instant processedAt;

    protected OutboxEvent() {
        // required by JPA
    }

    public OutboxEvent(String aggregateType, String aggregateId, String eventType, String payload) {
        this.aggregateType = aggregateType;
        this.aggregateId = aggregateId;
        this.eventType = eventType;
        this.payload = payload;
        this.createdAt = Instant.now();
        this.processed = false;
    }

    public void markProcessed() {
        this.processed = true;
        this.processedAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public String getAggregateType() {
        return aggregateType;
    }

    public String getAggregateId() {
        return aggregateId;
    }

    public String getEventType() {
        return eventType;
    }

    public String getPayload() {
        return payload;
    }

    public boolean isProcessed() {
        return processed;
    }
}
```

---

## File: src/main/java/com/example/outbox/outbox/OutboxRelay.java

```java
package com.example.outbox.outbox;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Limit;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * The "relay" (a.k.a. message relay / polling publisher). It periodically drains
 * the outbox table and forwards each event to Kafka, then marks it processed.
 *
 * Ordering matters: we wait for the broker to ACK BEFORE marking the row
 * processed. If the app crashes after the send but before the DB commit, the row
 * stays unprocessed and gets re-sent next tick — hence at-least-once delivery.
 * (Consumers should therefore be idempotent, e.g. key on eventType+userId.)
 */
@Component
public class OutboxRelay {

    private static final Logger log = LoggerFactory.getLogger(OutboxRelay.class);
    public static final String TOPIC = "user-events";
    private static final int BATCH_SIZE = 50;

    private final OutboxRepository outboxRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    public OutboxRelay(OutboxRepository outboxRepository, KafkaTemplate<String, String> kafkaTemplate) {
        this.outboxRepository = outboxRepository;
        this.kafkaTemplate = kafkaTemplate;
    }

    @Scheduled(fixedDelay = 2000) // poll every 2s (after the previous run finishes)
    @Transactional
    public void publishPending() {
        List<OutboxEvent> batch = outboxRepository.findByProcessedFalseOrderByIdAsc(Limit.of(BATCH_SIZE));
        if (batch.isEmpty()) {
            return;
        }
        log.info("[relay] found {} unprocessed outbox event(s)", batch.size());

        for (OutboxEvent event : batch) {
            try {
                SendResult<String, String> result = kafkaTemplate
                        .send(TOPIC, event.getAggregateId(), event.getPayload())
                        .get(10, TimeUnit.SECONDS); // block until Kafka acks

                event.markProcessed();
                log.info("[relay] published outbox id={} to {}-{} @offset {}",
                        event.getId(),
                        result.getRecordMetadata().topic(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset());
            } catch (Exception e) {
                // leave it unprocessed; next tick retries. Stop the batch so we
                // don't reorder this aggregate's events past a failure.
                log.warn("[relay] failed to publish outbox id={}, will retry", event.getId(), e);
                break;
            }
        }
        // processed flags flushed when this @Transactional method commits
    }
}
```

---

