# Observability Tools — Interview Cheatsheet

Observability = 3 pillars: **Traces** (request path across services), **Metrics** (numbers over time), **Logs** (event records). Everything below fits into one of these, or ties them together.

Natural order to learn this in: start at "how do I generate signals in my app" → "where do signals go" → "how do I see/query them" → "who sells this as a managed product".

---

## 1. Instrumentation layer: how signals get created

### Brave — the tracing library
Brave is a Java **tracer library**. It runs *inside your app*, wraps your HTTP/RPC calls, and generates trace/span IDs, propagates them via headers (`X-B3-*`), and records timing.

### Zipkin — the backend that stores/shows traces
Zipkin is a **standalone server + UI** that receives spans and lets you visualize a trace as a waterfall/flame graph across services.

**Why two of them?** Separation of concerns — Brave is the *client-side instrumentation* (runs in your JVM, has zero knowledge of storage), Zipkin is the *server-side collector+storage+UI* (has zero knowledge of your code). Brave sends spans to Zipkin over HTTP/Kafka. You could swap Brave for another B3-compatible tracer, or swap Zipkin's backend for another store — that's the point of decoupling them. (This mirrors OTEL's own SDK vs Collector split, described later — Brave+Zipkin is basically the pre-OTEL version of the same idea, Spring Cloud Sleuth used Brave under the hood.)

---

## 2. Metrics layer

### Micrometer — the metrics facade (the "SLF4J for metrics")
Micrometer is an **open-source metrics instrumentation facade**, built into Spring Boot (via `spring-boot-starter-actuator`). It's not a storage backend or UI itself — it's the library *inside your app* that records counters/timers/gauges (e.g., `http.server.requests`, JVM heap, Tomcat thread stats) using one vendor-neutral API, then exports them to whichever backend you plug in via a "registry" — Prometheus, Datadog, New Relic, CloudWatch, Graphite, etc. — just by adding a dependency, no code change.

**Why this matters / how it fits**: Micrometer is to metrics what Brave was to tracing, and what OTEL now tries to be for everything — an in-app facade decoupling instrumentation from backend choice. Concretely in a Spring Boot app: your code (or auto-instrumented framework code) records a metric via Micrometer → the `PrometheusMeterRegistry` formats it and exposes it on `/actuator/prometheus` → Prometheus scrapes that endpoint → Grafana visualizes it. Swap the registry to `DatadogMeterRegistry` and the same in-app metric now ships straight to Datadog instead — zero change to your business code.

**Interview soundbite**: "Micrometer is the vendor-neutral metrics API Spring Boot ships with by default; Prometheus/Datadog/etc. are just pluggable registries underneath it — same decoupling idea as Brave→Zipkin or OTEL SDK→Collector, just for the metrics pillar specifically." Also worth knowing: OTEL's metrics SDK and Micrometer overlap in purpose — Micrometer predates OTEL and is Spring's default, but Micrometer added an OTLP-exporting bridge so it can feed an OTEL Collector too if you want one unified pipeline for traces+metrics+logs.

### Prometheus
An **open-source metrics system**: time-series database + a query language (PromQL) + a "pull" scraper. Your app exposes a `/metrics` HTTP endpoint (numbers like request count, latency histograms, JVM heap), and Prometheus scrapes it on an interval and stores it. Prometheus itself has a bare-bones UI — not meant for pretty dashboards.

**Use case**: metrics only (not logs/traces), self-hosted, Kubernetes-native (it's the de facto standard for k8s monitoring).

### Grafana
An **open-source visualization/dashboarding layer** — it does NOT store data itself (mostly). It connects to data sources — Prometheus, Loki (logs), Tempo (traces), even Datadog/Splunk — and renders dashboards, alerts, graphs.

**Mental model**: Prometheus = the database, Grafana = the pretty face on top of it (and on top of many other things too).

---

## 3. All-in-one commercial platforms (the "buy vs build" alternative)

These bundle metrics + traces + logs + dashboards + alerting into one paid SaaS product, so you don't have to stitch Prometheus+Grafana+Zipkin+ELK yourself.

### Datadog
Commercial (not open-source). Agent-based (installs a "Datadog Agent" on hosts/containers) — collects metrics, traces, logs, infra monitoring, APM, all in one UI. Popular in cloud-native/microservices shops. Pricing scales with hosts/data volume, often a pain point.

### New Relic
Commercial (not open-source), similar positioning to Datadog — APM-first (Application Performance Monitoring), full-stack observability, its own agents per language. Historically strong for APM/deep code-level tracing (line-of-code visibility into slow transactions) before broadening into full observability.

### Splunk
Commercial (has a free tier), but originally a **log-analysis / SIEM tool**, not APM-first. Ingests massive volumes of unstructured log data, lets you search/query with SPL (Splunk's query language). Heavily used in security/ops/compliance contexts as well as observability. Splunk later acquired SignalFx to add metrics/APM.

**Interview framing**: Datadog/New Relic = APM-first commercial platforms that grew into full observability suites. Splunk = logs/SIEM-first platform that grew into observability. All three compete but come from different original centers of gravity.

---

## 4. OpenTelemetry (OTEL) — the vendor-neutral standardization layer

**What OTEL is**: a CNCF open-source **standard + SDK set** for generating and exporting traces, metrics, and logs, in a vendor-neutral format — so you instrument your code *once* and can send data to Zipkin, Prometheus, Datadog, New Relic, Splunk, or anything else, by just changing an "exporter" config, not your code.

It exists to kill the fragmentation of every vendor having its own proprietary instrumentation SDK (Brave for Zipkin, a Datadog-specific agent, a New Relic-specific agent, etc). OTEL is the industry converging on one instrumentation API.

### OTEL Agent (a.k.a. auto-instrumentation agent)
A Java (or other language) **javaagent** you attach to your app at startup (`-javaagent:opentelemetry-javaagent.jar`) that auto-instruments common frameworks (Spring, JDBC, HTTP clients) **without code changes** — captures traces/metrics automatically and emits them in OTLP (OpenTelemetry Protocol) format.

### OTEL Collector
A separate **standalone process/service** (like Zipkin was for Brave) that receives OTLP data from many apps' OTEL agents/SDKs, then can batch, filter, transform, and **fan it out to multiple backends** at once (e.g., send traces to Zipkin/Tempo, metrics to Prometheus, logs to Splunk, everything also to Datadog) via "exporters." It decouples your app from any single vendor.

**Relationship recap**: OTEL Agent/SDK (runs in-app, generates+exports signals) → OTEL Collector (receives, processes, routes) → any backend (Zipkin, Prometheus, Grafana stack, Datadog, New Relic, Splunk). This is the same Brave→Zipkin pattern, generalized and vendor-neutral, and now covers metrics+logs too, not just traces.

---

## 5. Other common tools worth knowing (with OSS status)

- **ELK / Elastic Stack** (Elasticsearch + Logstash + Kibana) — open-source (core; some features paid) log aggregation + search + visualization. The classic Splunk alternative.
- **Loki** — open-source, by Grafana Labs. "Prometheus for logs" — cheap log aggregation designed to pair with Grafana; indexes only metadata, not full text, so it's lighter than ELK.
- **Tempo** — open-source, by Grafana Labs. Trace storage backend designed to pair with Grafana (a modern alternative to Zipkin/Jaeger in the Grafana ecosystem).
- **Jaeger** — open-source (CNCF), originally Uber. Distributed tracing backend, direct alternative to Zipkin, native OTEL support.
- **Fluentd / Fluent Bit** — open-source log shippers/forwarders (collect logs from hosts/containers, forward to ELK/Splunk/Loki/etc.) — plays the same "collector" role for logs that OTEL Collector plays for traces/metrics.
- **PagerDuty / Opsgenie** — commercial, not observability data tools themselves but the alerting/on-call escalation layer that sits on top of Prometheus/Grafana/Datadog alerts.
- **AWS CloudWatch / GCP Cloud Monitoring / Azure Monitor** — commercial, cloud-native metrics+logs+traces built into each cloud provider — the "default" choice if you're all-in on one cloud and don't want extra tooling.
- **Honeycomb** — commercial, known for pioneering "high-cardinality" observability / trace-driven debugging (a different philosophy than dashboards-first tools).

---

## 6. Putting it all together (the mental model)

1. Your app needs to **produce** signals → instrument with **OTEL SDK/Agent** (modern, all 3 pillars) or per-pillar facades: **Micrometer** for metrics (Spring Boot default), Brave for tracing, or a vendor-specific agent (Datadog Agent, etc.).
2. Signals need to **travel and get processed** → **OTEL Collector** (vendor-neutral hub) or a vendor's own ingestion pipeline (Zipkin server, Datadog's backend, Splunk indexers, Fluentd).
3. Signals need to be **stored** → Prometheus (metrics), Zipkin/Tempo/Jaeger (traces), Elasticsearch/Loki/Splunk (logs), or a commercial vendor's proprietary store (Datadog/New Relic/Splunk).
4. Signals need to be **visualized/alerted on** → Grafana (open-source, multi-backend) or the vendor's built-in UI (Datadog/New Relic/Splunk dashboards).

**One-line recommendation per use case**:
- Fully open-source, self-hosted, k8s-native → Prometheus + Grafana + Loki + Tempo, all fed via OTEL Collector.
- Want zero infra to manage, willing to pay → Datadog or New Relic.
- Security/compliance-heavy log analysis → Splunk.
- Want to future-proof instrumentation against vendor lock-in → instrument with OTEL from day one regardless of backend.
- Legacy Spring app already using Sleuth/Brave/Zipkin → fine as-is, but new services should move to OTEL since Sleuth is effectively OTEL's predecessor and is in maintenance mode.
