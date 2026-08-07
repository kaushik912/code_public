# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/outbox/outbox/OutboxRepository.java

```java
package com.example.outbox.outbox;

import org.springframework.data.domain.Limit;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface OutboxRepository extends JpaRepository<OutboxEvent, Long> {

    /** The relay's query: oldest-first batch of events still waiting to be published. */
    List<OutboxEvent> findByProcessedFalseOrderByIdAsc(Limit limit);
}
```

---

## File: src/main/java/com/example/outbox/registration/RegisterController.java

```java
package com.example.outbox.registration;

import com.example.outbox.user.AppUser;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class RegisterController {

    private final RegistrationService registrationService;

    public RegisterController(RegistrationService registrationService) {
        this.registrationService = registrationService;
    }

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@Valid @RequestBody RegisterRequest request) {
        AppUser user = registrationService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "id", user.getId(),
                "username", user.getUsername(),
                "email", user.getEmail(),
                "note", "user + outbox event committed atomically; Kafka publish happens asynchronously"));
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, Object>> handleConflict(IllegalStateException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
    }
}
```

---

## File: src/main/java/com/example/outbox/registration/RegisterRequest.java

```java
package com.example.outbox.registration;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record RegisterRequest(
        @NotBlank String username,
        @NotBlank @Email String email) {
}
```

---

## File: src/main/java/com/example/outbox/registration/RegistrationService.java

```java
package com.example.outbox.registration;

import com.example.outbox.outbox.OutboxEvent;
import com.example.outbox.outbox.OutboxRepository;
import com.example.outbox.user.AppUser;
import com.example.outbox.user.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.ObjectNode;

@Service
public class RegistrationService {

    private final UserRepository userRepository;
    private final OutboxRepository outboxRepository;
    private final ObjectMapper objectMapper;

    public RegistrationService(UserRepository userRepository,
                               OutboxRepository outboxRepository,
                               ObjectMapper objectMapper) {
        this.userRepository = userRepository;
        this.outboxRepository = outboxRepository;
        this.objectMapper = objectMapper;
    }

    /**
     * The crux of the pattern: the user row AND the outbox row are written inside
     * ONE transaction. They commit together or not at all. We do NOT touch Kafka
     * here — publishing is deferred to the relay so a broker hiccup can never roll
     * back (or falsely commit) the registration.
     */
    @Transactional
    public AppUser register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.username())) {
            throw new IllegalStateException("username already taken: " + request.username());
        }

        // 1. business change
        AppUser user = userRepository.save(new AppUser(request.username(), request.email()));

        // 2. record the event to publish, in the SAME transaction
        String payload = toJson(user);
        outboxRepository.save(new OutboxEvent(
                "user",
                String.valueOf(user.getId()),
                "UserRegistered",
                payload));

        return user;
    }

    private String toJson(AppUser user) {
        // Jackson 3 (tools.jackson.*) throws unchecked JacksonException, so no try/catch needed.
        ObjectNode node = objectMapper.createObjectNode();
        node.put("eventType", "UserRegistered");
        node.put("userId", user.getId());
        node.put("username", user.getUsername());
        node.put("email", user.getEmail());
        node.put("registeredAt", user.getCreatedAt().toString());
        return objectMapper.writeValueAsString(node);
    }
}
```

---

## File: src/main/java/com/example/outbox/user/AppUser.java

```java
package com.example.outbox.user;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.Instant;

/**
 * The business aggregate. In this demo, registering a user must ALSO record an
 * outbox event — and both writes must land (or fail) together.
 */
@Entity
@Table(name = "app_user")
public class AppUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String email;

    @Column(nullable = false)
    private Instant createdAt;

    protected AppUser() {
        // required by JPA
    }

    public AppUser(String username, String email) {
        this.username = username;
        this.email = email;
        this.createdAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public String getEmail() {
        return email;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
```

---

