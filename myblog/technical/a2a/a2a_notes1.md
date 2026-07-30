# A2A Protocol (Agent2Agent)

**A2A** is an open protocol — originally introduced by Google in April 2025 and later donated to the Linux Foundation — for **agent-to-agent interoperability**. It lets autonomous AI agents built on *different* frameworks and by *different* vendors discover each other, delegate tasks, and collaborate over a standard HTTP interface.

## How it relates to MCP
They're complementary, not competing:
- **MCP** (Model Context Protocol) connects an agent to **tools, data, and resources** ("vertical" integration).
- **A2A** connects an agent to **other agents** as peers ("horizontal" integration).

## Core concepts

| Concept | Meaning |
|---|---|
| **Agent Card** | JSON metadata (served at `/.well-known/agent-card.json`) describing an agent's identity, skills, endpoint, and auth requirements. This is how agents are *discovered*. |
| **A2A Server** | An agent exposing an A2A-compliant HTTP endpoint. |
| **A2A Client** | An agent/app that consumes another agent. |
| **Task** | The central unit of work, with a lifecycle: `submitted → working → input-required → completed / failed / canceled`. |
| **Message** | One conversational turn; contains one or more **Parts**. |
| **Part** | Content unit: `TextPart`, `FilePart`, or `DataPart` (structured JSON). |
| **Artifact** | An output produced by the agent for a task. |

**Transport:** JSON-RPC 2.0 over HTTP(S). Supports **SSE streaming** (`message/stream`) and **push notifications** (webhooks) for long-running tasks. Key methods: `message/send`, `message/stream`, `tasks/get`, `tasks/cancel`.

---

## 1. Agent Card (discovery document)

Served at `https://my-agent.example.com/.well-known/agent-card.json`:

```json
{
  "name": "Currency Agent",
  "description": "Converts between currencies using live exchange rates.",
  "url": "https://my-agent.example.com/",
  "version": "1.0.0",
  "capabilities": { "streaming": true, "pushNotifications": false },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "convert_currency",
      "name": "Currency Conversion",
      "description": "Convert an amount from one currency to another.",
      "tags": ["finance", "currency"],
      "examples": ["Convert 100 USD to EUR"]
    }
  ]
}
```

---

## 2. Python server (using the official `a2a-sdk`)

```bash
pip install a2a-sdk uvicorn
```

```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    AgentCard, AgentSkill, AgentCapabilities,
)
import uvicorn


# 1. Your agent logic
class CurrencyAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input()
        # ... your real logic / LLM call here ...
        reply = f"You said: {user_text!r}. 100 USD ≈ 92 EUR."
        await event_queue.enqueue_event(new_agent_text_message(reply))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")


# 2. Describe the agent (the Agent Card)
skill = AgentSkill(
    id="convert_currency",
    name="Currency Conversion",
    description="Convert an amount from one currency to another.",
    tags=["finance", "currency"],
    examples=["Convert 100 USD to EUR"],
)

agent_card = AgentCard(
    name="Currency Agent",
    description="Converts between currencies using live exchange rates.",
    url="http://localhost:9999/",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[skill],
)

# 3. Wire up the server
handler = DefaultRequestHandler(
    agent_executor=CurrencyAgentExecutor(),
    task_store=InMemoryTaskStore(),
)
app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)

if __name__ == "__main__":
    uvicorn.run(app.build(), host="0.0.0.0", port=9999)
```

---

## 3. Python client

```python
import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import MessageSendParams, SendMessageRequest
from uuid import uuid4


async def main():
    base_url = "http://localhost:9999"
    async with httpx.AsyncClient() as httpx_client:
        # Discover the agent via its Agent Card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()

        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        # Send a message (JSON-RPC "message/send" under the hood)
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Convert 100 USD to EUR"}],
                    "messageId": uuid4().hex,
                }
            ),
        )
        response = await client.send_message(request)
        print(response.model_dump(mode="json", exclude_none=True))


import asyncio
asyncio.run(main())
```

---

## 4. Raw JSON-RPC (protocol-level view)

Everything above is a wrapper over a plain HTTP POST. This is what actually goes over the wire:

```bash
curl -X POST http://localhost:9999/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{ "kind": "text", "text": "Convert 100 USD to EUR" }],
        "messageId": "abc-123"
      }
    }
  }'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "kind": "message",
    "role": "agent",
    "parts": [{ "kind": "text", "text": "100 USD ≈ 92 EUR." }],
    "messageId": "def-456"
  }
}
```

For long-running work, you'd call `message/stream` instead and receive incremental `Task` status updates over SSE.

---

**Learn more:** the spec and SDKs live at the A2A project (`a2aproject/A2A` on GitHub, with `a2a-python`, `a2a-js`, etc.).

Want me to expand any part — e.g. a **streaming** example, **push-notification webhooks**, **multi-agent orchestration** (one agent calling several others), or an integration with a specific framework like LangGraph, CrewAI, or ADK?

## Short answer

**Yes — Java works fine.** You don't need Python. There's an **official `a2a-java` SDK** (from the A2A project, with Quarkus and Spring Boot flavors), *and* because A2A is just **JSON-RPC 2.0 over HTTP**, you can implement a compliant agent in plain Spring Boot with zero A2A dependencies. Given your background is Spring/Java, I'd start with the plain-Spring-Boot route — it's the best way to actually *see* what the protocol is doing.

## Suggested project: "Dad Joke Agent" 🎭

A minimal but complete E2E setup:

- **Agent server** (Spring Boot): serves an Agent Card + handles `message/send`, returns a joke.
- **Client** (a second tiny app or a `curl`): discovers the agent via its card, sends a message, prints the reply.

It needs no database, no external API, no auth — perfect for learning the request/response shape. You can later swap the joke logic for a real LLM call or a downstream service.

---

## Option A — Plain Spring Boot (recommended to learn)

**Agent Card** — serve at `/.well-known/agent-card.json`:

```java
@RestController
public class AgentCardController {

    @GetMapping("/.well-known/agent-card.json")
    public Map<String, Object> agentCard() {
        return Map.of(
            "name", "Dad Joke Agent",
            "description", "Tells dad jokes on demand.",
            "url", "http://localhost:8080/",
            "version", "1.0.0",
            "capabilities", Map.of("streaming", false, "pushNotifications", false),
            "defaultInputModes", List.of("text/plain"),
            "defaultOutputModes", List.of("text/plain"),
            "skills", List.of(Map.of(
                "id", "tell_joke",
                "name", "Tell a Joke",
                "description", "Returns a random dad joke.",
                "tags", List.of("fun", "humor"),
                "examples", List.of("Tell me a joke")
            ))
        );
    }
}
```

**JSON-RPC endpoint** — handles the `message/send` method:

```java
@RestController
public class A2AController {

    private static final List<String> JOKES = List.of(
        "I only know 25 letters of the alphabet. I don't know y.",
        "Why don't skeletons fight each other? They don't have the guts.",
        "I'm reading a book about anti-gravity. It's impossible to put down."
    );

    @PostMapping("/")
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String method = (String) req.get("method");
        Object id = req.get("id");

        if (!"message/send".equals(method)) {
            return Map.of("jsonrpc", "2.0", "id", id,
                "error", Map.of("code", -32601, "message", "Method not found"));
        }

        String joke = JOKES.get(new Random().nextInt(JOKES.size()));

        // A2A "message" result: role=agent, parts=[TextPart]
        Map<String, Object> result = Map.of(
            "kind", "message",
            "role", "agent",
            "messageId", UUID.randomUUID().toString(),
            "parts", List.of(Map.of("kind", "text", "text", joke))
        );

        return Map.of("jsonrpc", "2.0", "id", id, "result", result);
    }
}
```

**Test it E2E** with `curl` (this *is* a valid A2A client call):

```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Tell me a joke"}],"messageId":"m1"}}}'
```

**Or a Java client** (using JDK's `HttpClient`):

```java
public class JokeClient {
    public static void main(String[] args) throws Exception {
        var http = HttpClient.newHttpClient();

        // 1. Discover the agent
        var cardReq = HttpRequest.newBuilder()
            .uri(URI.create("http://localhost:8080/.well-known/agent-card.json"))
            .GET().build();
        System.out.println("Agent Card: " + http.send(cardReq, BodyHandlers.ofString()).body());

        // 2. Send a message
        String body = """
            {"jsonrpc":"2.0","id":"1","method":"message/send",
             "params":{"message":{"role":"user",
             "parts":[{"kind":"text","text":"Tell me a joke"}],"messageId":"m1"}}}""";
        var msgReq = HttpRequest.newBuilder()
            .uri(URI.create("http://localhost:8080/"))
            .header("Content-Type", "application/json")
            .POST(BodyHandlers.ofString(body)).build();  // BodyPublishers in real code
        System.out.println("Reply: " + http.send(msgReq, BodyHandlers.ofString()).body());
    }
}
```

*(In the client, use `HttpRequest.BodyPublishers.ofString(body)` for the POST body.)*

---

## Option B — Official `a2a-java` SDK

If you want the SDK to handle task lifecycle, streaming (SSE), and push notifications for you, add it via Maven:

```xml
<dependency>
    <groupId>io.a2a.sdk</groupId>
    <artifactId>a2a-java-sdk-server-common</artifactId>
    <version><!-- check latest on the a2aproject/a2a-java repo --></version>
</dependency>
```

You then implement an `AgentExecutor` (with `execute` / `cancel`) and expose an `AgentCard` bean — very similar in shape to the Python `AgentExecutor` I showed earlier. The SDK ships both **Quarkus** and **Spring Boot** transport modules. Repo: `a2aproject/a2a-java` on GitHub.

---

### My recommendation
Do **Option A first** — you'll fully understand the protocol in ~30 minutes with no SDK surprises — then migrate to **Option B** once you want streaming and proper task state management.

Want me to flesh this into a complete runnable Maven project (pom.xml + both apps), or add a **streaming (`message/stream` via SSE)** version in Java?

Excellent observation — and it's the key insight most A2A tutorials gloss over.

## A2A is the *envelope*, not the *letter*

A2A is deliberately "boring old HTTP." The protocol's only job is to let agents **find each other and pass messages** in a standard way. It contains **zero AI itself** — on purpose. The AI is whatever you drop *inside* the handler.

Think of it like REST: `@PostMapping` doesn't make something "AI." But if inside that method you call an LLM, *now* the endpoint is an agent. The AI shows up in **two distinct places**:

```
┌─────────────────┐         A2A (HTTP/JSON)         ┌─────────────────┐
│  HOST / CLIENT  │ ───────────────────────────────▶│  REMOTE AGENT   │
│                 │   "Tell me a joke about cats"    │                 │
│  🧠 LLM #1      │                                  │  🧠 LLM #2      │
│  decides WHICH  │◀─────────────────────────────── │  actually DOES  │
│  agent to call  │        joke text back            │  the work       │
└─────────────────┘                                  └─────────────────┘
   AI = routing/                                        AI = the skill
   orchestration
```

---

## Place 1: AI *inside* the agent (the executor)

Replace the hardcoded joke list with a real LLM call. Using **Spring AI** (idiomatic for a Spring dev):

```java
@RestController
public class A2AController {

    private final ChatClient chat;   // Spring AI — wraps OpenAI/Anthropic/etc.

    public A2AController(ChatClient.Builder builder) {
        this.chat = builder.build();
    }

    @PostMapping("/")
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        // 1. Pull the user's text out of the A2A message
        String userText = extractText(req);   // digs into params.message.parts[].text

        // 2. 🧠 THIS is where the AI lives now
        String answer = chat.prompt()
            .system("You are a witty comedian. Reply with one short joke.")
            .user(userText)
            .call()
            .content();

        // 3. Wrap the LLM output back into an A2A message
        Map<String, Object> result = Map.of(
            "kind", "message",
            "role", "agent",
            "messageId", UUID.randomUUID().toString(),
            "parts", List.of(Map.of("kind", "text", "text", answer))
        );
        return Map.of("jsonrpc", "2.0", "id", req.get("id"), "result", result);
    }
}
```

The controller/JSON-RPC scaffolding didn't change at all — it's still "old Java." But now the response is generated by an LLM. **That's the whole trick: A2A standardizes the wrapper so the AI inside is swappable and interoperable.**

---

## Place 2: AI *in the client* — this is the real payoff

The interesting AI isn't answering one agent — it's an **orchestrator LLM that reads Agent Cards and decides who to delegate to.** This is what makes A2A more than "just REST."

```java
// You have discovered several remote agents and fetched their Agent Cards:
List<AgentCard> availableAgents = List.of(
    jokeAgentCard,        // skills: tell_joke
    weatherAgentCard,     // skills: get_weather
    currencyAgentCard     // skills: convert_currency
);

// 🧠 The host LLM looks at the user's goal + the agent cards, and PICKS one
String userGoal = "Is it raining in Tokyo right now?";

String routingDecision = chat.prompt()
    .system("""
        You are a router. Given the user's request and this list of agents
        (with their skills), reply with ONLY the id of the best agent to handle it.
        Agents:
        %s
        """.formatted(summarize(availableAgents)))
    .user(userGoal)
    .call()
    .content();          // → "weather-agent"

// Then the client sends an A2A message/send to THAT agent's URL
AgentCard chosen = findById(availableAgents, routingDecision);
String reply = a2aClient.sendMessage(chosen.url(), userGoal);
```

Now the flow is genuinely agentic:
1. An LLM **reads capabilities** advertised in Agent Cards (discovery).
2. An LLM **decides which specialist agent** should handle the request (routing).
3. A2A **transports the delegation** in a standard format (so the weather agent could be written in Python by another team, deployed anywhere).
4. The remote agent's **own LLM** does the actual work.

---

## Why bother with the protocol at all?

You *could* just have your orchestrator call three private REST APIs. A2A adds value when:

| Without A2A | With A2A |
|---|---|
| You hardcode each downstream API's custom contract | Every agent speaks the **same** `message/send` shape |
| Discovery is manual/undocumented | Agents self-describe via **Agent Cards** (`/.well-known/agent-card.json`) |
| No standard for long-running tasks / streaming | Built-in **task lifecycle**, SSE streaming, push webhooks |
| Cross-team/cross-vendor integration is bespoke | A Python CrewAI agent and your Java Spring agent interoperate for free |

So: the "old Java controllers" *are* A2A — they're the standardized socket. The **AI is the LLM call you place inside the executor, and the LLM router you place inside the client.** The protocol just guarantees any two of those can talk without custom glue.

---

Want me to build the full **orchestrator + 2 specialist agents** example end-to-end in Java (with Spring AI wired to a real model), so you can see the multi-agent delegation actually run?

Here's a complete, **runnable single-project** version. Two specialist agents (joke + quote) and an orchestrator that routes between them — all A2A `message/send` under the hood.

## Spring Initializr dependencies

There is **no official "A2A" starter** in Spring Initializr — A2A is just JSON-RPC over HTTP, so all you actually need is:

| Dependency | Why |
|---|---|
| **Spring Web** (`spring-boot-starter-web`) | Controllers + the `RestClient` used to call other agents. **This is the only one required.** |
| **Spring AI – Anthropic/OpenAI** *(optional)* | Only if you want the orchestrator to route with an **LLM** instead of keywords. |
| **Lombok** *(optional)* | Convenience. |

> If you later want the *official* SDK's task-lifecycle/streaming, add it manually to `pom.xml` (not in Initializr):
> ```xml
> <dependency>
>   <groupId>io.a2a.sdk</groupId>
>   <artifactId>a2a-java-sdk-server-common</artifactId>
>   <version><!-- latest from a2aproject/a2a-java --></version>
> </dependency>
> ```

For this demo, **just pick "Spring Web."** Boot 3.2+ / Java 17+.

---

## Project structure

```
src/main/java/com/example/a2a/
├── A2aDemoApplication.java
├── JokeAgentController.java      // agent #1
├── QuoteAgentController.java     // agent #2
├── OrchestratorController.java   // host/router
└── A2aSupport.java               // tiny helpers
```

Everything runs in **one process on port 8080**. (In real A2A each agent is its own service with its card at the root `/.well-known/agent-card.json`; I'm namespacing under `/joke` and `/quote` so the demo runs as a single app. I note the difference below.)

---

### `A2aDemoApplication.java`

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

    @Bean
    RestClient restClient() {
        return RestClient.create();   // orchestrator uses this to call agents
    }
}
```

### `A2aSupport.java` — helpers to build/parse A2A messages

```java
package com.example.a2a;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public final class A2aSupport {

    /** Extract the user's text from an incoming A2A message/send request. */
    @SuppressWarnings("unchecked")
    static String userText(Map<String, Object> req) {
        var params  = (Map<String, Object>) req.get("params");
        var message = (Map<String, Object>) params.get("message");
        var parts   = (List<Map<String, Object>>) message.get("parts");
        return (String) parts.get(0).get("text");
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

    /** Build an outbound A2A message/send request body. */
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

### `JokeAgentController.java` — Agent #1

```java
package com.example.a2a;

import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/joke")
public class JokeAgentController {

    private static final List<String> JOKES = List.of(
        "I only know 25 letters of the alphabet. I don't know y.",
        "Why don't skeletons fight each other? They don't have the guts.",
        "I'm reading a book about anti-gravity — it's impossible to put down."
    );
    private final Random random = new Random();

    // A2A discovery: the Agent Card
    @GetMapping("/.well-known/agent-card.json")
    public Map<String, Object> card() {
        return Map.of(
            "name", "Joke Agent",
            "description", "Returns a random joke.",
            "url", "http://localhost:8080/joke",
            "version", "1.0.0",
            "capabilities", Map.of("streaming", false),
            "skills", List.of(Map.of(
                "id", "tell_joke", "name", "Tell a Joke",
                "description", "Returns a random joke.",
                "tags", List.of("fun", "humor", "joke")))
        );
    }

    // A2A JSON-RPC endpoint
    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String joke = JOKES.get(random.nextInt(JOKES.size()));
        return A2aSupport.reply(req.get("id"), joke);
    }
}
```

### `QuoteAgentController.java` — Agent #2

```java
package com.example.a2a;

import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/quote")
public class QuoteAgentController {

    private static final List<String> QUOTES = List.of(
        "\"The only way to do great work is to love what you do.\" — Steve Jobs",
        "\"Simplicity is the soul of efficiency.\" — Austin Freeman",
        "\"Talk is cheap. Show me the code.\" — Linus Torvalds"
    );
    private final Random random = new Random();

    @GetMapping("/.well-known/agent-card.json")
    public Map<String, Object> card() {
        return Map.of(
            "name", "Quote Agent",
            "description", "Returns a random inspirational quote.",
            "url", "http://localhost:8080/quote",
            "version", "1.0.0",
            "capabilities", Map.of("streaming", false),
            "skills", List.of(Map.of(
                "id", "give_quote", "name", "Give a Quote",
                "description", "Returns a random inspirational quote.",
                "tags", List.of("inspiration", "motivation", "quote")))
        );
    }

    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String quote = QUOTES.get(random.nextInt(QUOTES.size()));
        return A2aSupport.reply(req.get("id"), quote);
    }
}
```

### `OrchestratorController.java` — the router (this is the "AI" seat)

```java
package com.example.a2a;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import java.util.*;

@RestController
public class OrchestratorController {

    private final RestClient http;

    // Registry of known agents (in real A2A you'd fetch these cards at startup)
    private static final Map<String, String> AGENTS = Map.of(
        "joke-agent",  "http://localhost:8080/joke",
        "quote-agent", "http://localhost:8080/quote"
    );

    public OrchestratorController(RestClient http) {
        this.http = http;
    }

    @GetMapping("/ask")
    public Map<String, Object> ask(@RequestParam String q) {
        // 1. ROUTE — decide which agent handles this
        String agentId = route(q);
        String agentUrl = AGENTS.get(agentId);

        // 2. DELEGATE via A2A message/send
        Map<String, Object> response = http.post()
            .uri(agentUrl)
            .body(A2aSupport.sendRequest(q))
            .retrieve()
            .body(Map.class);

        // 3. Unwrap the agent's reply
        String answer = A2aSupport.userText(
            Map.of("params", Map.of("message", ((Map) response.get("result")))));

        return Map.of("routedTo", agentId, "answer", answer);
    }

    /**
     * The routing decision. Keyword-based so it runs with zero API keys.
     * ↓↓↓ Swap this method body for an LLM call to make it truly agentic ↓↓↓
     */
    private String route(String query) {
        String q = query.toLowerCase();
        if (q.contains("quote") || q.contains("inspire") || q.contains("motivat"))
            return "quote-agent";
        return "joke-agent";   // default
    }
}
```

---

## Run & test

```bash
./mvnw spring-boot:run
```

```bash
curl "http://localhost:8080/ask?q=tell%20me%20a%20joke"
```
```json
{ "routedTo": "joke-agent", "answer": "I only know 25 letters of the alphabet. I don't know y." }
```

```bash
curl "http://localhost:8080/ask?q=give%20me%20an%20inspiring%20quote"
```
```json
{ "routedTo": "quote-agent", "answer": "\"Talk is cheap. Show me the code.\" — Linus Torvalds" }
```

You can also hit the agents directly (proving they're independent A2A services):

```bash
curl http://localhost:8080/joke/.well-known/agent-card.json
```

---

## Making the router actually "AI"

Replace the `route(...)` method with an LLM call. Add **Spring AI (Anthropic)** to `pom.xml`, inject `ChatClient`, and:

```java
private String route(String query) {
    return chatClient.prompt()
        .system("""
            Reply with ONLY one agent id that best handles the user's request.
            Options:
            - joke-agent  (skills: tell jokes, humor)
            - quote-agent (skills: inspirational quotes, motivation)
            """)
        .user(query)
        .call()
        .content()
        .trim();
}
```

Now the orchestrator *reasons* over the agents' advertised skills instead of matching keywords — and because it speaks A2A, either agent could later be replaced by a Python service on another host with **no change to this code**.

---

**Two things I simplified for a single runnable app** (worth knowing for "real" A2A):
1. Each agent should be its **own deployable service** with its card at the **root** `/.well-known/agent-card.json` — I namespaced under `/joke` and `/quote` so it's one process.
2. The orchestrator here has a hardcoded registry; a full client fetches each Agent Card at startup and feeds those skills to the LLM router dynamically.

Want me to split this into **three separate Spring Boot modules** (true multi-service, each on its own port with root-level cards), or wire the **Spring AI LLM router** in fully with a working `pom.xml`?

Perfect use case — this is exactly what Spring AI's abstraction buys you: **the `ChatClient` code stays identical; you only swap the dependency + config.** Ollama runs models locally, so there are no API keys at all.

## 1. Install Ollama & pull a model (one-time)

```bash
# install from ollama.com, then:
ollama pull llama3.2
ollama serve        # runs at http://localhost:11434
```

A small model like `llama3.2` (3B) is plenty for routing decisions.

## 2. Swap the dependency

Remove the Anthropic starter, add the **Ollama** one. With Spring AI 1.0:

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-ollama</artifactId>
</dependency>
```

And the Spring AI BOM in `<dependencyManagement>` (so you don't pin the version yourself):

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-bom</artifactId>
      <version>1.0.0</version>   <!-- use the latest 1.0.x -->
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

> Note: the artifact name changed at 1.0. If you're on a pre-1.0 milestone it's `spring-ai-ollama-spring-boot-starter` instead. Spring AI is also on Spring Initializr under **"Ollama"** (in the AI section) — you can just tick that box.

## 3. Configure `application.properties`

```properties
spring.ai.ollama.base-url=http://localhost:11434
spring.ai.ollama.chat.options.model=llama3.2
spring.ai.ollama.chat.options.temperature=0.0
# Optional: auto-pull the model on startup if missing
spring.ai.ollama.init.pull-model-strategy=when_missing
```

## 4. Your code doesn't change

The orchestrator's router is **byte-for-byte the same** as the Anthropic version — that's the whole point of the abstraction:

```java
@RestController
public class OrchestratorController {

    private final ChatClient chat;
    private final RestClient http;

    public OrchestratorController(ChatClient.Builder builder, RestClient http) {
        this.chat = builder.build();   // now backed by Ollama, transparently
        this.http = http;
    }

    private String route(String query) {
        return chat.prompt()
            .system("""
                Reply with ONLY one agent id that best handles the user's request.
                Options:
                - joke-agent  (skills: tell jokes, humor)
                - quote-agent (skills: inspirational quotes, motivation)
                Output just the id, nothing else.
                """)
            .user(query)
            .call()
            .content()
            .trim();
    }
    // ... /ask endpoint unchanged ...
}
```

Spring AI auto-configures an `OllamaChatModel` from the properties and injects it into `ChatClient.Builder`. Switching providers = changing one dependency + one properties block.

---

## Two practical tips for local models

1. **Constrain the output.** Small local models sometimes add chatter ("Sure! The best agent is joke-agent."). Defend against it:
   ```java
   String raw = chat.prompt()...call().content().toLowerCase();
   String agentId = raw.contains("quote") ? "quote-agent" : "joke-agent";
   ```
   Or use Spring AI's **structured output** to force a clean enum/JSON response.

2. **`temperature=0.0`** for routing — you want deterministic classification, not creativity.

---

## Sidebar: Ollama for the *agents* too

You could make the **joke/quote agents themselves** LLM-powered by giving each its own `ChatClient` — even pointing different agents at **different models** (e.g. joke agent on `llama3.2`, quote agent on `mistral`). Each agent's `application.properties` picks its model; A2A doesn't care what's behind the endpoint. That's the interoperability payoff: one Ollama agent, one Anthropic agent, and one Python agent can all sit behind the same orchestrator.

Want me to convert the joke and quote agents to generate their content via Ollama as well, or keep them as the simple random-list versions?

Here's the full LLM-powered version, with **each agent running its own model** to show the interoperability point.

## Pull the models

```bash
ollama pull llama3.2   # joke agent + orchestrator
ollama pull mistral    # quote agent
```

## 1. `AiConfig.java` — one `ChatClient` per model

Because we want *different* models in the same app, we build the beans manually instead of relying on the single auto-configured one:

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiConfig {

    @Bean
    OllamaApi ollamaApi() {
        return OllamaApi.builder().baseUrl("http://localhost:11434").build();
    }

    private ChatClient client(OllamaApi api, String model, double temp) {
        OllamaChatModel chatModel = OllamaChatModel.builder()
            .ollamaApi(api)
            .defaultOptions(OllamaOptions.builder()
                .model(model)
                .temperature(temp)
                .build())
            .build();
        return ChatClient.create(chatModel);
    }

    @Bean("jokeChatClient")
    ChatClient jokeChatClient(OllamaApi api) {
        return client(api, "llama3.2", 0.9);   // creative → varied jokes
    }

    @Bean("quoteChatClient")
    ChatClient quoteChatClient(OllamaApi api) {
        return client(api, "mistral", 0.8);     // different model entirely
    }

    @Bean("routerChatClient")
    ChatClient routerChatClient(OllamaApi api) {
        return client(api, "llama3.2", 0.0);    // deterministic → routing
    }
}
```

## 2. `JokeAgentController.java` — now LLM-generated

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;
import java.util.*;

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
            "skills", List.of(Map.of(
                "id", "tell_joke", "name", "Tell a Joke",
                "description", "Returns a fresh joke.",
                "tags", List.of("fun", "humor", "joke")))
        );
    }

    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String userText = A2aSupport.userText(req);   // what the caller asked for

        String joke = chat.prompt()
            .system("You are a comedian. Respond with exactly ONE short, original joke. No preamble.")
            .user(userText.isBlank() ? "Tell me a random joke." : userText)
            .call()
            .content()
            .trim();

        return A2aSupport.reply(req.get("id"), joke);
    }
}
```

## 3. `QuoteAgentController.java` — LLM-generated, different model

```java
package com.example.a2a;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;
import java.util.*;

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
            "skills", List.of(Map.of(
                "id", "give_quote", "name", "Give a Quote",
                "description", "Returns an inspirational quote.",
                "tags", List.of("inspiration", "motivation", "quote")))
        );
    }

    @PostMapping
    public Map<String, Object> handle(@RequestBody Map<String, Object> req) {
        String userText = A2aSupport.userText(req);

        String quote = chat.prompt()
            .system("Respond with exactly ONE short inspirational quote and its author. Format: \"quote\" — Author. No preamble.")
            .user(userText.isBlank() ? "Give me an inspiring quote." : userText)
            .call()
            .content()
            .trim();

        return A2aSupport.reply(req.get("id"), quote);
    }
}
```

## 4. Orchestrator — inject the router client

Update just the constructor to use the qualified router bean:

```java
public OrchestratorController(@Qualifier("routerChatClient") ChatClient chat,
                              RestClient http) {
    this.chat = chat;
    this.http = http;
}
```

The `route(...)` and `/ask` methods stay exactly as before.

---

## Run & test

```bash
ollama serve            # make sure it's up
./mvnw spring-boot:run
```

```bash
curl "http://localhost:8080/ask?q=make%20me%20laugh"
```
```json
{ "routedTo": "joke-agent",
  "answer": "Why did the developer go broke? Because he used up all his cache." }
```

```bash
curl "http://localhost:8080/ask?q=I%20need%20some%20motivation%20today"
```
```json
{ "routedTo": "quote-agent",
  "answer": "\"Discipline is the bridge between goals and accomplishment.\" — Jim Rohn" }
```

Each request now flows: **orchestrator (llama3.2, temp 0) routes → agent (llama3.2 or mistral) generates → A2A carries the reply back.**

---

## What you just built

```
                       ┌────────────────────────────┐
   /ask?q=...  ───────▶│ Orchestrator                │
                       │  🧠 llama3.2 (temp 0) routes │
                       └───────┬──────────────┬───────┘
                    A2A msg    │              │   A2A msg
                    /send      ▼              ▼   /send
              ┌──────────────────┐   ┌──────────────────┐
              │ Joke Agent       │   │ Quote Agent      │
              │  🧠 llama3.2      │   │  🧠 mistral       │
              └──────────────────┘   └──────────────────┘
```

Three agents, **two different models**, one protocol. Swapping any agent to Anthropic, OpenAI, or a Python service means changing *that agent only* — the orchestrator and the A2A wire format never change.

---

## Two caveats for local models
1. **Quotes may be fabricated.** LLMs invent plausible-sounding quotes and misattribute them. For real quotes, keep the static list (or have the agent call a quotes API/DB) — this is a great spot for **MCP** (the agent uses an MCP tool to fetch a real quote, then A2A returns it).
2. **Latency.** First call after startup is slow while Ollama loads the model into memory; subsequent calls are fast.

Want me to add **streaming** (`message/stream` via SSE so the joke types out token-by-token), or wire one agent to a real **MCP tool** to show A2A + MCP working together?
