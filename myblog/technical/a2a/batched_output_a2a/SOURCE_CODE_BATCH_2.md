# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/a2a/JokeAgentController.java

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * A2A Agent #1 — generates a joke with an LLM (llama3.2).
 * Discovery card at: /joke/.well-known/agent-card.json
 * JSON-RPC endpoint : POST /joke
 */
@RestController
@RequestMapping("/joke")
public class JokeAgentController {

    private final ChatClient chat;

    public JokeAgentController(@Qualifier("jokeChatClient") ChatClient chat) {
        this.chat = chat;
    }

    @GetMapping("/.well-known/agent-card.json")
    public Map<String, Object> card() {
        return Map.of(
            "name", "Joke Agent",
            "description", "Generates a random joke with an LLM.",
            "url", "http://localhost:8080/joke",
            "version", "1.0.0",
            "capabilities", Map.of("streaming", false),
            "defaultInputModes", List.of("text/plain"),
            "defaultOutputModes", List.of("text/plain"),
            "skills", List.of(Map.of(
                "id", "tell_joke",
                "name", "Tell a Joke",
                "description", "Returns a fresh joke.",
                "tags", List.of("fun", "humor", "joke")))
        );
    }

    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String userText = A2aSupport.userText(req);

        // A fixed prompt + fixed seed makes the model return the same joke every
        // time. For generic asks, seed a random topic so each call differs.
        String prompt;
        String lower = userText.toLowerCase();
        boolean generic = userText.isBlank()
            || lower.contains("laugh") || lower.contains("random")
            || lower.matches(".*\\btell me a joke\\b.*") || lower.equals("joke");
        if (generic) {
            String topic = TOPICS.get(random.nextInt(TOPICS.size()));
            prompt = "Tell me a short, original joke about " + topic + ".";
        } else {
            prompt = userText;   // respect a specific request, e.g. "joke about cats"
        }

        String joke = chat.prompt()
            .system("You are a comedian. Respond with exactly ONE short, original joke. No preamble, no explanation.")
            .user(prompt)
            .call()
            .content()
            .trim();

        return A2aSupport.reply(req.get("id"), joke);
    }

    private static final List<String> TOPICS = List.of(
        "cats", "programming", "coffee", "Mondays", "robots", "pizza",
        "the ocean", "music", "space", "dad life", "cars", "weather");

    private final java.util.Random random = new java.util.Random();
}
```

---

## File: src/main/java/com/example/a2a/OrchestratorController.java

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

import java.util.Map;

/**
 * The host / orchestrator. An LLM decides which agent should handle the
 * request, then it delegates via an A2A "message/send" call.
 */
@RestController
public class OrchestratorController {

    private final ChatClient router;
    private final RestClient http;

    /** Known agents. In full A2A you'd fetch these cards at startup. */
    private static final Map<String, String> AGENTS = Map.of(
        "joke-agent",  "http://localhost:8080/joke",
        "quote-agent", "http://localhost:8080/quote"
    );

    public OrchestratorController(@Qualifier("routerChatClient") ChatClient router,
                                  RestClient http) {
        this.router = router;
        this.http = http;
    }

    @GetMapping("/ask")
    @SuppressWarnings("unchecked")
    public Map<String, Object> ask(@RequestParam String q) {
        // 1. ROUTE — the LLM picks the best agent for this request.
        String agentId = route(q);
        String agentUrl = AGENTS.get(agentId);

        // 2. DELEGATE — send an A2A message/send to the chosen agent.
        Map<String, Object> response = http.post()
            .uri(agentUrl)
            .body(A2aSupport.sendRequest(q))
            .retrieve()
            .body(Map.class);

        // 3. UNWRAP the agent's reply and return it.
        String answer = A2aSupport.answerText(response);
        return Map.of("routedTo", agentId, "answer", answer);
    }

    /**
     * LLM-based routing. Kept defensive: small local models sometimes add
     * chatter, so we look for keywords in the model's output rather than
     * trusting an exact id.
     */
    private String route(String query) {
        String decision = router.prompt()
            .system("""
                You are a router. Reply with ONLY one agent id that best handles
                the user's request. Output just the id, nothing else.
                Options:
                - joke-agent  (skills: tell jokes, humor)
                - quote-agent (skills: inspirational quotes, motivation)
                """)
            .user(query)
            .call()
            .content()
            .toLowerCase();

        return decision.contains("quote") ? "quote-agent" : "joke-agent";
    }
}
```

---

## File: src/main/java/com/example/a2a/QuoteAgentController.java

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * A2A Agent #2 — generates an inspirational quote with an LLM (mistral).
 * Discovery card at: /quote/.well-known/agent-card.json
 * JSON-RPC endpoint : POST /quote
 */
@RestController
@RequestMapping("/quote")
public class QuoteAgentController {

    private final ChatClient chat;

    public QuoteAgentController(@Qualifier("quoteChatClient") ChatClient chat) {
        this.chat = chat;
    }

    @GetMapping("/.well-known/agent-card.json")
    public Map<String, Object> card() {
        return Map.of(
            "name", "Quote Agent",
            "description", "Generates an inspirational quote with an LLM.",
            "url", "http://localhost:8080/quote",
            "version", "1.0.0",
            "capabilities", Map.of("streaming", false),
            "defaultInputModes", List.of("text/plain"),
            "defaultOutputModes", List.of("text/plain"),
            "skills", List.of(Map.of(
                "id", "give_quote",
                "name", "Give a Quote",
                "description", "Returns an inspirational quote.",
                "tags", List.of("inspiration", "motivation", "quote")))
        );
    }

    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String userText = A2aSupport.userText(req);

        String quote = chat.prompt()
            .system("Respond with exactly ONE short inspirational quote and its author. "
                + "Format: \"quote\" - Author. No preamble.")
            .user(userText.isBlank() ? "Give me an inspiring quote." : userText)
            .call()
            .content()
            .trim();

        return A2aSupport.reply(req.get("id"), quote);
    }
}
```

---

## File: src/main/java/com/example/a2a/llm/AnthropicModelFactory.java

```java
package com.example.a2a.llm;

import org.springframework.ai.anthropic.AnthropicChatModel;
import org.springframework.ai.anthropic.AnthropicChatOptions;
import org.springframework.ai.anthropic.api.AnthropicApi;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/** Anthropic (Claude) models. Activated when a2a.llm.provider=anthropic. */
@Component
public class AnthropicModelFactory implements ChatModelFactory {

    private final String apiKey;
    private final String model;

    public AnthropicModelFactory(
            @Value("${spring.ai.anthropic.api-key:}") String apiKey,
            @Value("${a2a.llm.anthropic.model:claude-sonnet-5}") String model) {
        this.apiKey = apiKey;
        this.model = model;
    }

    @Override
    public String provider() {
        return "anthropic";
    }

    @Override
    public ChatModel create(double temperature) {
        AnthropicApi api = AnthropicApi.builder().apiKey(apiKey).build();
        return AnthropicChatModel.builder()
            .anthropicApi(api)
            .defaultOptions(AnthropicChatOptions.builder()
                .model(model)
                .temperature(temperature)
                .build())
            .build();
    }
}
```

---

## File: src/main/java/com/example/a2a/llm/ChatModelFactory.java

```java
package com.example.a2a.llm;

import org.springframework.ai.chat.model.ChatModel;

/**
 * Factory abstraction over LLM providers. Each implementation knows how to
 * build a provider-specific {@link ChatModel}. The active one is selected at
 * runtime by the {@code a2a.llm.provider} property (see AiConfig).
 */
public interface ChatModelFactory {

    /** Provider id this factory handles, e.g. "ollama", "openai", "anthropic". */
    String provider();

    /** Build a ChatModel using this provider's configured model + given temperature. */
    ChatModel create(double temperature);
}
```

---

