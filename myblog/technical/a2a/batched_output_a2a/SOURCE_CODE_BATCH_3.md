# Source Code Batch

This file contains 4 source files.

---

## File: src/main/java/com/example/a2a/llm/OllamaModelFactory.java

```java
package com.example.a2a.llm;

import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/** Local models via Ollama. This is the default provider. */
@Component
public class OllamaModelFactory implements ChatModelFactory {

    private final String baseUrl;
    private final String model;

    public OllamaModelFactory(
            @Value("${a2a.llm.ollama.base-url:http://localhost:11434}") String baseUrl,
            @Value("${a2a.llm.ollama.model:mistral}") String model) {
        this.baseUrl = baseUrl;
        this.model = model;
    }

    @Override
    public String provider() {
        return "ollama";
    }

    @Override
    public ChatModel create(double temperature) {
        OllamaApi api = OllamaApi.builder().baseUrl(baseUrl).build();
        return OllamaChatModel.builder()
            .ollamaApi(api)
            .defaultOptions(OllamaOptions.builder()
                .model(model)
                .temperature(temperature)
                .build())
            .build();
    }
}
```

---

## File: src/main/java/com/example/a2a/llm/OpenAiModelFactory.java

```java
package com.example.a2a.llm;

import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/** OpenAI (or OpenAI-compatible) models. Activated when a2a.llm.provider=openai. */
@Component
public class OpenAiModelFactory implements ChatModelFactory {

    private final String apiKey;
    private final String model;

    public OpenAiModelFactory(
            @Value("${spring.ai.openai.api-key:}") String apiKey,
            @Value("${a2a.llm.openai.model:gpt-4o-mini}") String model) {
        this.apiKey = apiKey;
        this.model = model;
    }

    @Override
    public String provider() {
        return "openai";
    }

    @Override
    public ChatModel create(double temperature) {
        OpenAiApi api = OpenAiApi.builder().apiKey(apiKey).build();
        return OpenAiChatModel.builder()
            .openAiApi(api)
            .defaultOptions(OpenAiChatOptions.builder()
                .model(model)
                .temperature(temperature)
                .build())
            .build();
    }
}
```

---

## File: src/main/resources/application.properties

```
spring.application.name=a2a-hello-world
server.port=8080

# We build ChatModels ourselves via the ChatModelFactory, so turn OFF Spring AI's
# chat-model auto-configuration. This prevents unused providers (e.g. OpenAI /
# Anthropic) from demanding an API key at startup.
spring.ai.model.chat=none

# ======================================================================
# Provider switch — the factory selects the implementation by this value.
# Options: ollama (default) | openai | anthropic
# ======================================================================
a2a.llm.provider=ollama

# ---- Ollama (local, default) ----
a2a.llm.ollama.base-url=http://localhost:11434
a2a.llm.ollama.model=llama3.1

# ---- OpenAI (used only when a2a.llm.provider=openai) ----
# Spring AI's auto-config validates this key is PRESENT at startup even when the
# provider is unused. The "not-used" placeholder satisfies that check (it never
# authenticates — no OpenAI call is made unless you select provider=openai).
# When you actually use OpenAI, export OPENAI_API_KEY and it takes over.
spring.ai.openai.api-key=${OPENAI_API_KEY:not-used}
a2a.llm.openai.model=gpt-4o-mini

# ---- Anthropic (used only when a2a.llm.provider=anthropic) ----
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY:not-used}
a2a.llm.anthropic.model=claude-sonnet-5
```

---

## File: target/classes/application.properties

```
spring.application.name=a2a-hello-world
server.port=8080

# We build ChatModels ourselves via the ChatModelFactory, so turn OFF Spring AI's
# chat-model auto-configuration. This prevents unused providers (e.g. OpenAI /
# Anthropic) from demanding an API key at startup.
spring.ai.model.chat=none

# ======================================================================
# Provider switch — the factory selects the implementation by this value.
# Options: ollama (default) | openai | anthropic
# ======================================================================
a2a.llm.provider=ollama

# ---- Ollama (local, default) ----
a2a.llm.ollama.base-url=http://localhost:11434
a2a.llm.ollama.model=llama3.1

# ---- OpenAI (used only when a2a.llm.provider=openai) ----
# Spring AI's auto-config validates this key is PRESENT at startup even when the
# provider is unused. The "not-used" placeholder satisfies that check (it never
# authenticates — no OpenAI call is made unless you select provider=openai).
# When you actually use OpenAI, export OPENAI_API_KEY and it takes over.
spring.ai.openai.api-key=${OPENAI_API_KEY:not-used}
a2a.llm.openai.model=gpt-4o-mini

# ---- Anthropic (used only when a2a.llm.provider=anthropic) ----
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY:not-used}
a2a.llm.anthropic.model=claude-sonnet-5
```

---

