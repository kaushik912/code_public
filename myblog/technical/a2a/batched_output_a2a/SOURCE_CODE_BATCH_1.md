# Source Code Batch

This file contains 5 source files.

---

## File: README.md

```markdown
# A2A Hello World (Spring Boot + Ollama)

A minimal **Agent2Agent (A2A)** demo: an orchestrator routes requests to one of
two specialist agents over the A2A protocol (JSON-RPC 2.0 over HTTP).

```
   /ask?q=...  ──▶  Orchestrator (llama3.2, routes)
                        │
              A2A message/send
                        ├──▶  Joke Agent   (llama3.2)
                        └──▶  Quote Agent  (mistral)
```

All three run in one Spring Boot process on port 8080. In real A2A each agent
is its own service with its card served at the root `/.well-known/agent-card.json`;
here they are namespaced under `/joke` and `/quote` so the demo is one app.

## Prerequisites

1. **Java 17+** and **Maven** (or use the wrapper if you add one).
2. **Ollama** running locally with the two models pulled:

```bash
ollama serve
ollama pull llama3.2
ollama pull mistral
```

## Run

```bash
mvn spring-boot:run
```

## Try it

Route to the joke agent:

```bash
curl "http://localhost:8080/ask?q=make%20me%20laugh"
```

Route to the quote agent:

```bash
curl "http://localhost:8080/ask?q=I%20need%20some%20motivation%20today"
```

Hit an agent directly (proves it's a standalone A2A service):

```bash
curl http://localhost:8080/joke/.well-known/agent-card.json

curl -X POST http://localhost:8080/joke \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"tell me a joke"}],"messageId":"m1"}}}'
```

## Switching LLM provider (factory pattern)

The provider is chosen by one property — no code changes. Edit
`application.properties` (or pass `-D` / env override):

```properties
a2a.llm.provider=ollama     # default; local models
# a2a.llm.provider=openai   # needs OPENAI_API_KEY
# a2a.llm.provider=anthropic# needs ANTHROPIC_API_KEY
```

Or at run time:

```bash
OPENAI_API_KEY=sk-... mvn spring-boot:run -Dspring-boot.run.arguments=--a2a.llm.provider=openai
```

How it works: `ChatModelFactory` has one implementation per provider
(`OllamaModelFactory`, `OpenAiModelFactory`, `AnthropicModelFactory`), each
tagged with its `provider()` id. `AiConfig` injects all of them and picks the
one matching `a2a.llm.provider`. An unknown value fails fast at startup with the
list of valid providers.

## Notes

- **Quotes may be fabricated** — LLMs invent/misattribute quotes. For real ones,
  back the agent with a static list or a quotes API/MCP tool.
- First request after startup is slow while Ollama loads the model into memory.
```

---

## File: pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.4.1</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>a2a-hello-world</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>a2a-hello-world</name>
    <description>A2A hello-world: orchestrator + joke agent + quote agent, powered by Ollama</description>

    <properties>
        <java.version>17</java.version>
        <spring-ai.version>1.0.0</spring-ai.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.ai</groupId>
                <artifactId>spring-ai-bom</artifactId>
                <version>${spring-ai.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!--
          All three provider modules are on the classpath so the factory can
          build any of them. We disable Spring AI's chat auto-config
          (spring.ai.model.chat=none) and build ChatModels ourselves, so no
          API key is required for providers you aren't using.
        -->
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-model-ollama</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-model-openai</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-model-anthropic</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
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

## File: src/main/java/com/example/a2a/A2aDemoApplication.java

```java
package com.example.a2a;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class A2aDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(A2aDemoApplication.class, args);
    }

    /** Used by the orchestrator to make outbound A2A calls to the agents. */
    @Bean
    RestClient restClient() {
        return RestClient.create();
    }
}
```

---

## File: src/main/java/com/example/a2a/A2aSupport.java

```java
package com.example.a2a;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Tiny helpers for building and parsing A2A (Agent2Agent) JSON-RPC messages.
 * A2A is just JSON-RPC 2.0 over HTTP, so these are plain Map manipulations.
 */
public final class A2aSupport {

    private A2aSupport() {
    }

    /** Extract the user's text from an incoming A2A "message/send" request. */
    @SuppressWarnings("unchecked")
    static String userText(Map<String, Object> req) {
        Map<String, Object> params = (Map<String, Object>) req.get("params");
        Map<String, Object> message = (Map<String, Object>) params.get("message");
        List<Map<String, Object>> parts = (List<Map<String, Object>>) message.get("parts");
        Object text = parts.get(0).get("text");
        return text == null ? "" : text.toString();
    }

    /** Extract the agent's reply text from a JSON-RPC response body. */
    @SuppressWarnings("unchecked")
    static String answerText(Map<String, Object> response) {
        Map<String, Object> result = (Map<String, Object>) response.get("result");
        List<Map<String, Object>> parts = (List<Map<String, Object>>) result.get("parts");
        Object text = parts.get(0).get("text");
        return text == null ? "" : text.toString();
    }

    /** Wrap an agent's answer into a JSON-RPC A2A "message" result. */
    static Map<String, Object> reply(Object requestId, String text) {
        return Map.of(
            "jsonrpc", "2.0",
            "id", requestId,
            "result", Map.of(
                "kind", "message",
                "role", "agent",
                "messageId", UUID.randomUUID().toString(),
                "parts", List.of(Map.of("kind", "text", "text", text))
            )
        );
    }

    /** Build an outbound A2A "message/send" request body. */
    static Map<String, Object> sendRequest(String text) {
        return Map.of(
            "jsonrpc", "2.0",
            "id", UUID.randomUUID().toString(),
            "method", "message/send",
            "params", Map.of("message", Map.of(
                "role", "user",
                "messageId", UUID.randomUUID().toString(),
                "parts", List.of(Map.of("kind", "text", "text", text))
            ))
        );
    }
}
```

---

## File: src/main/java/com/example/a2a/AiConfig.java

```java
package com.example.a2a;

import com.example.a2a.llm.ChatModelFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * Selects an LLM provider via the {@code a2a.llm.provider} property (default
 * "ollama") and builds one ChatClient per role. Spring injects every
 * {@link ChatModelFactory} on the classpath; we pick the one whose
 * {@link ChatModelFactory#provider()} matches the configured value.
 *
 * Swapping providers is now pure configuration — no code changes here.
 */
@Configuration
public class AiConfig {

    private final ChatModelFactory factory;

    public AiConfig(List<ChatModelFactory> factories,
                    @Value("${a2a.llm.provider:ollama}") String provider) {
        this.factory = factories.stream()
            .filter(f -> f.provider().equalsIgnoreCase(provider))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException(
                "Unknown a2a.llm.provider='" + provider + "'. Available: "
                    + factories.stream().map(ChatModelFactory::provider).toList()));
    }

    @Bean("jokeChatClient")
    ChatClient jokeChatClient() {
        return ChatClient.create(factory.create(0.9));   // creative -> varied jokes
    }

    @Bean("quoteChatClient")
    ChatClient quoteChatClient() {
        return ChatClient.create(factory.create(0.8));
    }

    @Bean("routerChatClient")
    ChatClient routerChatClient() {
        return ChatClient.create(factory.create(0.0));   // deterministic -> routing
    }
}
```

---

