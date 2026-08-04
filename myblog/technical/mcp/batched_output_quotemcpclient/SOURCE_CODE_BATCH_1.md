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

## File: README.md

```markdown
# MCP Learning Setup — Quote Server + LLM Client

A minimal, end-to-end **Model Context Protocol (MCP)** playground built with Spring Boot 4.1 + Spring AI 2.0.

- **`randomquote/`** — an MCP **server** that exposes a `randomQuote` tool (and a plain REST endpoint).
- **`mcp-client/`** (this project) — an MCP **host**: it owns the LLMs (Ollama + Anthropic), connects to the server, discovers its tools, and lets the model decide when to call them.

---

## The one mental model

> **MCP is USB for tools.** A *server* advertises capabilities and executes them; a *host* with an LLM discovers and calls them over a standard wire. Tool selection is the LLM's job, driven by the tool **description** — never keyword matching.

```
  "get me a random quote"
          │
          ▼
   ┌──────────────┐   tool descriptions    ┌───────────────┐
   │  LLM (host)  │ ◀───────────────────── │  mcp-client   │  :8081
   │ Ollama/Claude│  decides to call tool  │  (MCP client) │
   └──────┬───────┘ ─────────────────────▶ └──────┬────────┘
          │                                        │  JSON-RPC over HTTP/SSE
      final answer                                 │  (tools/list, tools/call)
                                                    ▼
                                            ┌───────────────┐
                                            │  randomquote  │  :8080
                                            │  (MCP server) │  @Tool randomQuote()
                                            └───────────────┘
```

Two layers, kept separate:
- **Transport** (`/sse` + `/mcp/message`, JSON-RPC) = dumb pipe + directory. Framework's job.
- **Selection** (LLM reads descriptions, decides) = the intelligence. The model's job.

---

## What a developer actually writes

Only three things per tool — the rest is framework:

1. **A method** (`getRandomQuote()`) — normal code.
2. **A description** (`@Tool(description = "...")`) — the only MCP-specific skill; it's how the LLM finds the tool.
3. **Registration** (`ToolCallbackProvider` bean) — boilerplate.

```java
@Tool(description = "Returns a random inspirational quote")
public String randomQuote() { return quoteService.getRandomQuote(); }
```

---

## Run it

**Prerequisites:** Java 17, Maven (wrapper included), [Ollama](https://ollama.com) running with `mistral` pulled.

```bash
# 1. pull the local model
ollama pull mistral

# 2. start the MCP server (terminal 1)
cd randomquote && ./mvnw spring-boot:run        # → http://localhost:8080

# 3. start the MCP client (terminal 2)
cd mcp-client && ./mvnw spring-boot:run         # → http://localhost:8081
```

Anthropic is wired with a dummy key by default. To use it for real:
```bash
export ANTHROPIC_API_KEY=sk-ant-...   # then /chat/anthropic works, zero code change
```

---

## Endpoints

### Server — `randomquote` (:8080)
| Method | Path | Purpose |
|---|---|---|
| GET | `/randomQuote` | plain REST — same logic, no MCP |
| GET | `/sse` | MCP SSE stream (server→client) |
| POST | `/mcp/message` | MCP messages (client→server) |

### Client — `mcp-client` (:8081)
| Method | Path | Purpose |
|---|---|---|
| GET | `/tools` | list tools discovered from the server (proves wiring) |
| GET | `/chat/ollama?q=...` | Mistral decides whether to call the tool |
| GET | `/chat/anthropic?q=...` | Claude decides (needs real API key) |

```bash
curl "http://localhost:8081/tools"
# ["randomQuote : Returns a random inspirational quote"]

curl "http://localhost:8081/chat/ollama?q=get%20me%20a%20random%20quote"
# Here's a quote: "Simplicity is the soul of efficiency. — Austin Freeman"
```

---

## How the wire works (for debugging)

MCP is JSON-RPC. Two methods matter:

| JSON-RPC method | When | Isolates |
|---|---|---|
| `initialize` | on connect | transport / connectivity |
| `tools/list` | at startup | is the tool **registered + described**? |
| `tools/call` | when LLM decides | does the tool **run**? |

**Debug ladder** — walk top-down; first broken rung names the layer:

1. **Tool log fires?** (add `log.info(...)` in the `@Tool` method) → did *my code* run? *Ground truth.*
2. **Tool in `/tools`?** → is it registered/discovered?
3. **LLM won't call a listed tool?** → **description problem**, not a bug. Sharpen it.
4. **`tools/call` errors/times out?** → your method threw or blocked; check logs.

Test the server without any LLM: **MCP Inspector** → `npx @modelcontextprotocol/inspector` → connect to `http://localhost:8080/sse` → Tools tab.

Wire it into a real host (Claude Desktop / Copilot) via the SSE bridge:
```json
{ "mcpServers": { "random-quote": {
    "command": "npx", "args": ["mcp-remote", "http://localhost:8080/sse"] } } }
```

---

## Key design notes

- **Config `quotes` ≠ tool `randomQuote`.** `spring.ai.mcp.client.sse.connections.quotes.url` maps a *label* to a *URL*. The tool name is learned at runtime via `tools/list` — never configured. Add tools to the server and the client picks them up with no config change.
- **Two models, injected by type.** `ChatController` injects `OllamaChatModel` + `AnthropicChatModel` directly (not `ChatClient.Builder`) — with two chat models present, the builder auto-config backs off (`ConditionalOnSingleCandidate`), so injecting concrete models avoids ambiguity. Same MCP tools handed to both — only the brain differs.
- **Missing the connection config?** Best case the app fails fast (no `ToolCallbackProvider` bean → startup error); worst case it boots toolless and the LLM silently answers without the tool. The tool-side log line (ladder step 1) distinguishes the two.

---

## Caveats

- **Local-model reliability:** small models (Mistral 7B) sometimes decline to call a fitting tool or return empty content after a call. Mitigate with a sharp description, low `temperature`, or a system-prompt nudge (`"you MUST use the randomQuote tool"`). Hosted models (Claude) are far more reliable.
- **Ports:** server 8080, client 8081 — don't collide.
- **`netty-resolver-dns-native-macos` warning** at client boot is cosmetic.
- **VPN:** the corporate Maven mirror (and first-time dependency downloads) require VPN.
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
		<relativePath/>
	</parent>
	<groupId>com.example</groupId>
	<artifactId>mcp-client</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>mcp-client</name>
	<description>MCP client: Ollama + Anthropic, connects to the quote MCP server</description>

	<properties>
		<java.version>17</java.version>
		<spring-ai.version>2.0.0</spring-ai.version>
	</properties>

	<dependencies>
		<!-- web layer for the /chat endpoints -->
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc</artifactId>
		</dependency>

		<!-- MCP client: discovers tools from remote MCP servers over SSE -->
		<dependency>
			<groupId>org.springframework.ai</groupId>
			<artifactId>spring-ai-starter-mcp-client-webflux</artifactId>
		</dependency>

		<!-- two chat models: the LLM decides whether to call the tool -->
		<dependency>
			<groupId>org.springframework.ai</groupId>
			<artifactId>spring-ai-starter-model-ollama</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.ai</groupId>
			<artifactId>spring-ai-starter-model-anthropic</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>

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

## File: src/main/java/com/example/mcpclient/ChatController.java

```java
package com.example.mcpclient;

import java.util.Arrays;
import java.util.List;

import org.springframework.ai.anthropic.AnthropicChatModel;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * The "host" side of MCP: it owns the LLMs and lets them decide whether to call
 * the tools discovered from the remote quote MCP server.
 *
 * Two concrete model beans are injected by type (OllamaChatModel,
 * AnthropicChatModel) — that sidesteps the ChatClient.Builder ambiguity you'd
 * hit if you injected the builder while two chat models are on the classpath.
 *
 * `mcpTools` is the ToolCallbackProvider auto-created by the MCP client
 * autoconfig: at startup it connected to the server(s) in application.properties,
 * ran tools/list, and wrapped the results. We never name "randomQuote" here —
 * it is discovered.
 */
@RestController
public class ChatController {

    private final ChatClient ollamaClient;
    private final ChatClient anthropicClient;
    private final ToolCallbackProvider mcpTools;

    public ChatController(OllamaChatModel ollamaModel,
                          AnthropicChatModel anthropicModel,
                          ToolCallbackProvider mcpTools) {
        this.mcpTools = mcpTools;
        // same MCP tools handed to both models — only the brain differs
        this.ollamaClient = ChatClient.builder(ollamaModel)
                .defaultToolCallbacks(mcpTools)
                .build();
        this.anthropicClient = ChatClient.builder(anthropicModel)
                .defaultToolCallbacks(mcpTools)
                .build();
    }

    @GetMapping("/chat/ollama")
    public String ollama(@RequestParam String q) {
        return ollamaClient.prompt().user(q).call().content();
    }

    @GetMapping("/chat/anthropic")
    public String anthropic(@RequestParam String q) {
        return anthropicClient.prompt().user(q).call().content();
    }

    /** Debug: what tools were discovered from the MCP server(s) at startup? */
    @GetMapping("/tools")
    public List<String> tools() {
        return Arrays.stream(mcpTools.getToolCallbacks())
                .map(tc -> tc.getToolDefinition().name() + " : " + tc.getToolDefinition().description())
                .toList();
    }
}
```

---

## File: src/main/java/com/example/mcpclient/McpClientApplication.java

```java
package com.example.mcpclient;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class McpClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpClientApplication.class, args);
    }
}
```

---

