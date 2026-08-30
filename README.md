# AI Engineering Portfolio: Agents, RAG, MCP & Spring AI

A working engineer's AI-agent stack, built one standalone repo at a time — not a single mega-project, but a deliberate set of focused builds, each one nailing down a specific piece: tool discovery, agent-to-agent delegation, RAG, memory, resilience. All linked repos are public, runnable, and on GitHub.

If you're an interviewer skimming this: every project below is real code with a README and a `mvn`/`docker` command that works, not slideware. Anchored in a Java/Spring background, extended into the current AI-agent ecosystem.

## Top 10 projects

All original (non-forked) work, all public on GitHub.

### 1. [mcp-quote-server](https://github.com/kaushik912/mcp-quote-server) — a minimal MCP tool server
Exposes one tool (`randomQuote`) over SSE using `spring-ai-starter-mcp-server-webmvc` — the "server" half of the MCP protocol, kept deliberately small so the contract (`tools/list`, tool call/result) is easy to point to.

### 2. [mcp-quote-client](https://github.com/kaushik912/mcp-quote-client) — MCP host, three interchangeable brains
Connects to `mcp-quote-server`, discovers its tools at startup, and hands the *same* toolset to three separate `ChatClient`s — Ollama (local), Anthropic, and Gemini (via Spring AI's OpenAI-compatible starter) — so the LLM decides per-request whether to call the tool, purely from its description. Mental model stated explicitly in the README: **"MCP is USB for tools."**

**Talking points (1+2):** host/server separation, tool selection is a model decision (not keyword routing), swapping the "brain" behind an identical toolset to compare providers.

### 3. [weathermcp](https://github.com/kaushik912/weathermcp) — provider-agnostic agent with multi-server MCP tool discovery
A Python agent (FastAPI + LiteLLM) that aggregates tools from *two independent* MCP servers (weather, quotes) and routes each tool call back to the server that owns it — new tools require zero changes to the agent. LiteLLM makes the model itself a one-line swap (`anthropic/claude-sonnet-5` → `ollama/llama3.1` → any of ~100 providers), so neither the model nor the toolset is hardcoded anywhere in the app.

**Talking points:** aggregating tools across multiple MCP servers, provider-agnostic model layer via LiteLLM, "reason → act → observe" agent loop from scratch (no framework).

### 4. [research-agent-news-tool](https://github.com/kaushik912/research-agent-news-tool) — companion MCP server
A `searchNews` tool exposed over SSE, standing in for a real news API behind a stable tool contract — the server half of project 5.

### 5. [research-agent](https://github.com/kaushik912/research-agent) — full agent: RAG + memory + MCP tools, wired together
Implements a published reference architecture (ChatClient + MCP tool calling + RAG + session memory) end to end on Gemini. `MessageChatMemoryAdvisor` gives it per-session conversation history, `QuestionAnswerAdvisor` injects retrieved docs from an in-memory vector store, and MCP tool callbacks — discovered at startup from `research-agent-news-tool` — let the model decide when to call `searchNews`. The README documents a real bug hit and fixed: Gemini's OpenAI-compatible `/embeddings` endpoint omits a field the strict `openai-java` client requires, so embeddings are routed through Spring AI's native Gemini module instead.

**Talking points (4+5):** composing three advisor/tool concerns into one `ChatClient`, debugging a cross-vendor API compatibility gap instead of just swallowing the error, MCP client/server split across two services.

### 6. [a2a-hello-world](https://github.com/kaushik912/a2a-hello-world) — Agent2Agent protocol, implemented not just documented
A working A2A (Agent2Agent) system: an orchestrator that routes a query to one of two specialist agents by asking an LLM (temp 0.0) to pick, then sends a real `message/send` JSON-RPC 2.0 call to that agent's URL and unwraps the reply — no A2A SDK, hand-rolled request/response helpers, to see the actual wire protocol. LLM provider is pluggable per agent (`ollama` / `openai` / `anthropic`) via a `ChatModelFactory`, and each agent exposes a discovery card at `/.well-known/agent-card.json`.

**Talking points:** A2A vs. MCP (agent-to-agent vs. agent-to-tool), building the protocol layer by hand before reaching for an SDK, per-agent model pluggability.

### 7. [resilience-llm-failover](https://github.com/kaushik912/resilience-llm-failover) — treating an LLM provider like any other flaky dependency
A Spring Boot POC that routes chat requests to Gemini by default and automatically fails over to OpenRouter when Gemini is rate-limited, using Resilience4j's `@CircuitBreaker` — plus Swagger/OpenAPI docs out of the box. It applies standard backend resilience patterns to an LLM call instead of treating "call the model" as a special case.

**Talking points:** circuit breakers applied to LLM providers, multi-provider failover as a reliability concern (not just a cost-optimization one), Resilience4j in a Spring Boot service.

### 8. [claude_orchestrator](https://github.com/kaushik912/claude_orchestrator) — tooling that drives AI agents, not just calls them
A headless runner that batches prompts through the `claude` CLI — single files, a directory of `.md` prompts, or an ordered JSON workflow spec — executing each with `stream-json` output parsing, per-prompt timeouts, and full logging, wired to run unattended off a cron schedule. It's the meta layer: instead of writing another app that calls an LLM, this is infrastructure for running *many* agent invocations reliably and repeatably.

**Talking points:** building infra around agentic CLIs rather than just using them interactively, batch/cron-driven AI workflows, treating agent runs as something you log and audit.

### 9. [my-claude-skills](https://github.com/kaushik912/my-claude-skills) — authoring reusable capabilities for a coding agent
A version-controlled library of custom Claude Code skills — structured instruction sets an agent loads on demand rather than being told from scratch each time. Includes a spec-driven feature workflow (`spec`/`ticket-spec`: spec → plan → tasks → TDD implementation, resumable from disk state, never from memory of an earlier turn), a Spring Boot project-init generator, a Postman→Bruno script converter, and a free-tier-LLM picker — plus checked-in security/Spring rules the agent must follow. This very README was produced by an agent operating under those rules.

**Talking points:** treating agent behavior as versioned, testable configuration rather than ad hoc prompting; designing skills to be resumable from on-disk state (never trusted memory) for safe parallel/unattended runs.

### 10. [langchain-learning-lab](https://github.com/kaushik912/langchain-learning-lab) — LangChain v1 / LangGraph fundamentals, runnable
A from-scratch Python port of a LangChain course, rebuilt on the current LangChain v1/LangGraph API (`StateGraph`s with a checkpointer, not the deprecated `AgentExecutor`/`RunnableWithMessageHistory`) — numbered example folders covering LCEL, prompt templates, embeddings/vector stores, RAG, chat memory, sequential workflows, and agents, with concept docs kept separate from code.

**Talking points:** migrating off deprecated LangChain APIs onto `StateGraph`, keeping runnable examples separate from prose explanation, breadth across the LangChain/LangGraph fundamentals independent of the Java/Spring stack.

---

## Why this matters for a Spring/Java role with AI ambitions

Most "AI experience" on a resume is a single `openai.ChatCompletion.create()` call. This portfolio instead treats AI features as **systems problems**: protocol design (A2A, MCP), resilience (circuit breakers, failover), composability (advisors, memory, RAG, tools), and workflow infrastructure — the same rigor you'd bring to any backend system, applied to agents. Deeper dives and design notes behind several of these builds live in this repo under [`technical/a2a`](technical/a2a), [`technical/mcp`](technical/mcp), [`technical/spring/spring-orchestrator`](technical/spring/spring-orchestrator), and [`technical/genai`](technical/genai).

---

# Repository purpose

This repository is a personal collection of technical notes, end-to-end (E2E) guides and quick-reference material maintained for learning and practical recall. It is meant as a learning aid and a ready-reckoner for common patterns, gotchas and walkthroughs.

Key points:
- Learning-focused: curated notes, tips and examples to help understand concepts quickly.
- E2E guides: practical walkthroughs that can be followed start-to-finish for common tasks.
- Quick references: short notes and "cheat-sheet" style pages for fast lookup.

License / Use
- This repo is intended for personal learning and sharing. Verify and test any steps before using in production.
