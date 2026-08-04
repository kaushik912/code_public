# Source Code Batch

This file contains 1 source files.

---

## File: src/main/resources/application.properties

```
spring.application.name=mcp-client

# run on 8081 so we don't collide with the quote MCP server on 8080
server.port=8081
# webflux is on the classpath (MCP client transport uses WebClient) -> force servlet
spring.main.web-application-type=servlet

# ---- MCP client: connect to the quote server and discover its tools ----
# "quotes" is just a label for this connection; the tool name (randomQuote)
# is learned at runtime via tools/list, NOT configured here.
spring.ai.mcp.client.sse.connections.quotes.url=http://localhost:8080
spring.ai.mcp.client.toolcallback.enabled=true
spring.ai.mcp.client.type=SYNC
spring.ai.mcp.client.request-timeout=30s

# ---- Ollama (local, real) ----
spring.ai.ollama.base-url=http://localhost:11434
spring.ai.ollama.chat.options.model=mistral
spring.ai.ollama.chat.options.temperature=0.1

# ---- Anthropic (DUMMY key for now: app boots, /chat/anthropic will 401 until real key) ----
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY:dummy-key-replace-me}
spring.ai.anthropic.chat.options.model=claude-sonnet-5
```

---

