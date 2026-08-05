Great pairing to ask about together, because they're the classic **monitoring stack** — and they map directly onto the time-series concepts from the start of our chat. In one line: **Prometheus collects and stores the metrics; Grafana displays them.**

## Prometheus — the time-series database + collector

Prometheus answers: *"What is happening in my systems right now, and how has it changed over time?"* It's a **time-series database** (exactly the kind we discussed) specialized for **metrics** — numbers over time like CPU %, memory, request rate, error count, latency.

Two things make it distinctive:

**1. It pulls, not receives (scraping).** Instead of your apps pushing data in, Prometheus **reaches out and "scrapes"** each service's `/metrics` endpoint every few seconds. Your app just exposes numbers; Prometheus goes and grabs them on a schedule.

```
your-service:8080/metrics   ← Prometheus scrapes this every 15s
  http_requests_total{status="200"}  14523
  http_requests_total{status="500"}  12
  memory_usage_bytes                 734003200
```

**2. It has its own query language — PromQL.** You ask time-based questions:
```
rate(http_requests_total[5m])          # requests per second over last 5 min
histogram_quantile(0.95, latency)      # 95th-percentile latency
```

It also does **alerting** — "fire an alert if error rate > 1% for 5 minutes" — via Alertmanager.

## Grafana — the visualization / dashboard layer

Grafana answers: *"Show me all of that on a screen I can actually read."* It's a **dashboarding tool** that connects to a data source (Prometheus, but also Timescale, ClickHouse, Postgres, Elasticsearch, and many more), runs queries, and renders **graphs, gauges, heatmaps, tables, and alerts** on shared dashboards.

Crucially, **Grafana stores almost no data itself** — it's a window onto data that lives elsewhere. It queries Prometheus live and draws the results.

## How they work together

```
┌────────────┐   scrapes    ┌──────────────┐   queries    ┌──────────┐
│ your apps   │ ───────────▶ │  Prometheus   │ ◀─────────── │ Grafana   │
│ /metrics    │   (pull)     │ (stores TSDB) │   (PromQL)   │ dashboards│
└────────────┘              └──────────────┘              └──────────┘
                                    │
                                    ▼ rules
                              Alertmanager → Slack / PagerDuty
```

1. Apps expose metrics at `/metrics`
2. **Prometheus scrapes and stores** them as time-series
3. **Grafana queries Prometheus** and draws dashboards
4. **Alerts** fire when thresholds are crossed → notify Slack/PagerDuty

Think of it as: **Prometheus = the memory (data + facts over time)**, **Grafana = the eyes (how you see it)**. They're separate tools precisely so you can swap either side — Grafana can visualize other databases; Prometheus can feed other frontends.

## Tie-back to your CI/CD project

Remember the last point — running pipelines produces **execution metrics and logs**, an append-only time-series workload. That's exactly this stack's job:

- Your CI/CD service exposes metrics: `pipeline_runs_total`, `pipeline_duration_seconds`, `pipeline_failures_total{project="x"}`
- **Prometheus** scrapes and stores them
- **Grafana** shows a dashboard: success rate over 30 days, average build time per project, current running pipelines
- **Alert**: "notify #oncall if pipeline failure rate > 10% in the last 15 min"

So Prometheus + Grafana would be a natural fit for the **operational monitoring** side of your Harness-like tool (how the *system* is doing), separate from Postgres storing the pipeline definitions and ClickHouse/S3 handling run history and logs.

## One-liner

**Prometheus** is a time-series database that scrapes and stores metrics and raises alerts; **Grafana** is the dashboard tool that queries those metrics (and other data sources) and turns them into readable graphs. Together they're the go-to open-source stack for **monitoring what your systems are doing over time.**

Not at all — that's a common misconception. Prometheus doesn't care *what* the number means; it stores **any numeric time-series.** System metrics (CPU, RAM) are just the most common example because infra tools ship them out of the box. **Business metrics work exactly the same way** — you just have to expose them yourself.

## Prometheus stores numbers, not "system stats"

To Prometheus, these are all identical — just a named number with labels, sampled over time:

```
# infra metric
memory_usage_bytes                              734003200

# business metrics — same mechanism
orders_placed_total{country="US"}               14523
revenue_dollars_total{plan="pro"}               98230
signups_total{source="google"}                  412
checkout_failures_total{reason="card_declined"} 37
active_users                                     1841
```

You emit these from your application code (via a Prometheus client library), Prometheus scrapes them, and now you can graph "orders per minute" or alert on "signups dropped to zero" — same as any infra metric.

## What business questions this answers well

```
rate(orders_placed_total[5m])                    # orders per second, live
sum(revenue_dollars_total) by (plan)             # revenue split by plan
increase(signups_total[1h])                      # signups in the last hour
```

Great for **operational business monitoring** — real-time, aggregate trends you want on a dashboard or an alert:
- "Orders per minute just dropped 80% — is checkout broken?"
- "Signup rate by traffic source, live"
- "Alert if revenue/hour falls below X"

This is genuinely valuable — teams catch outages *by watching business metrics* (a sudden drop in orders detects a bug faster than a CPU graph).

## The real limits (this is the important part)

Prometheus is for **aggregatable numeric metrics**, not a business *database of record*. Two hard boundaries:

**1. It's dimensional aggregates, not individual records.** Prometheus knows *"14,523 orders placed,"* not *"order #8842 by user Ana for $59.99 at 10:03."* It stores counts and gauges, **not the orders themselves.** For per-order detail, revenue reconciliation, or "show me this customer's order history," you need Postgres / a data warehouse.

**2. Beware high cardinality — the classic Prometheus killer.** Labels must have **few distinct values** (`plan="pro|free"`, `country="US|UK"` — fine). Never put **unbounded** values like `user_id`, `order_id`, `email`, or `session_id` in a label:

```
# ❌ DISASTER — one time-series per user, millions of them → Prometheus falls over
orders_total{user_id="8842", order_id="a91f..."}

# ✅ FINE — a handful of label values
orders_total{plan="pro", country="US"}
```

This is the cardinality problem we flagged earlier, and it's the #1 way people break Prometheus with business data. Metrics = low-cardinality aggregates. Per-entity detail = wrong tool.

## So who does what for business data

| Question | Tool |
|---|---|
| "Orders per minute right now / alert if it drops" | ✅ **Prometheus + Grafana** (real-time aggregate) |
| "Exact revenue last quarter, per customer, reconciled" | ❌ **Data warehouse** (BigQuery/Snowflake/ClickHouse) |
| "Show order #8842's line items" | ❌ **Postgres** (system of record) |
| "Analyze individual events with many dimensions" | ❌ **OLAP / warehouse** |

There's a natural split: **Prometheus for real-time operational monitoring** (is the business *functioning* right now?), and a **data warehouse for precise business analytics/BI** (what exactly happened, per record, for reporting and finance).

## One-liner

Prometheus isn't limited to RAM/CPU — it happily stores **business metrics** too, as long as they're **low-cardinality numeric aggregates** (orders/sec, signups/hour, revenue by plan). What it *isn't* is a store of individual business records or a source for exact, per-entity reporting — that's a data warehouse's or Postgres's job. Use Prometheus to answer *"is the business healthy right now?"*, not *"what exactly did customer X buy?"*
