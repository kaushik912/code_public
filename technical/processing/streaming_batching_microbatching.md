# Streaming, Batching, Micro-Batching — Crash Course

The whole topic comes down to **one question**: *when you have a stream of incoming data, how many records do you wait for before you do work?*

- **Batch** → wait for a *lot* (or all of it), then process in one big shot.
- **Streaming** → process *each record* the moment it arrives.
- **Micro-batch** → wait for a *tiny group* (a few ms/seconds worth), then process that group. A pragmatic middle ground.

Everything else — latency, throughput, cost, complexity — falls out of that one dial.

---

## 1. Batching

**Idea:** Collect data over a window (an hour, a day, "all of it"), then run a job over the whole set at once.

**Mental model:** doing all your laundry Sunday night instead of washing each sock as it gets dirty.

| Property | Value |
|---|---|
| Latency | High (minutes → hours → days) |
| Throughput | **Highest** — amortizes overhead, enables bulk optimizations (sorting, joins, columnar scans) |
| Complexity | Lowest — bounded input, no "what about late data?" |
| Cost efficiency | Best per-record |

**Why it's efficient:** fixed costs (spinning up a job, opening a DB connection, a full-table scan, a JVM warmup) get spread across millions of rows. A `JOIN` over a whole day's data is far cheaper per-row than a million single-row lookups.

**Real-life use cases:**
- **Payroll / billing runs** — you *want* to wait until the period closes. Nobody needs a paycheck computed per-second.
- **Nightly ETL / data-warehouse loads** — ingest the day's transactions into Snowflake/BigQuery at 2 AM.
- **Your own world:** the TAC **ARR/ASV recalculation** or a nightly golden-metrics regeneration is naturally batch — recompute all opportunities in one pass, correctness over latency.
- **ML model training** — churn over the full historical dataset.
- **Report generation** — monthly financial close, invoices.

**When to pick it:** results have a natural deadline (end of day/month), correctness/completeness matters more than freshness, and volume is huge.

---

## 2. Streaming (record-at-a-time / event-at-a-time)

**Idea:** Process each event as it arrives. The pipeline is *always on*; data is unbounded and never "done."

**Mental model:** a bartender serving each customer as they walk up, not waiting for the bar to fill.

| Property | Value |
|---|---|
| Latency | **Lowest** (ms) |
| Throughput | Lower per-record (per-event overhead) |
| Complexity | **Highest** — must handle out-of-order events, late data, exactly-once semantics, state, failures mid-stream |
| Cost | Higher — always-running infrastructure |

**The hard parts** (this is where streaming gets its reputation): windowing (how do you "sum the last 5 minutes" over an infinite stream?), late/out-of-order events (event happened at 12:00 but arrived at 12:03), and fault tolerance (crash halfway — did that event get counted?).

**Real-life use cases:**
- **Fraud detection** — a card swipe must be blocked *now*, not in tomorrow's batch.
- **Live dashboards / observability** — Splunk-style log ingestion, metrics, alerting the second an error spikes.
- **Real-time bidding (ad tech)** — you have ~100ms to decide a bid.
- **IoT / telemetry** — sensor readings triggering an alarm when a temperature crosses a threshold.
- **Notifications / chat / presence** — deliver the message as it's sent.

**Tech:** Apache Flink (true per-event), Kafka Streams, ksqlDB.

**When to pick it:** the value of the data decays in seconds, or an action must be taken immediately.

---

## 3. Micro-Batching

**Idea:** Streaming's usability with batch's efficiency. Buffer events for a very short window (say 200ms–5s) or until N records accumulate, then process that small batch. Repeat forever.

**Mental model:** the bartender waits ~10 seconds, serves everyone currently in line together, then repeats — not per-person, not once-a-night.

| Property | Value |
|---|---|
| Latency | Low-ish (seconds) — *near* real-time, not real-time |
| Throughput | High — regains bulk efficiencies |
| Complexity | Medium — reuses batch machinery on a loop |
| Cost | Moderate |

**Why it exists:** true per-event streaming is expensive and complex. Most "real-time" business needs are fine with a 1–5 second delay. Micro-batching gives you *most* of the latency benefit while letting you do efficient bulk writes (e.g. one DB `INSERT` of 500 rows instead of 500 inserts).

**Real-life use cases:**
- **Spark Structured Streaming** — the canonical example; it's micro-batch under the hood (Continuous mode aside).
- **Near-real-time analytics** — "sales in the last few seconds" dashboards where 2s lag is invisible to a human.
- **Log/metrics shippers** — Fluentd/Logstash flushing buffered events every few seconds.
- **Bulk API sinks** — batching writes to Elasticsearch, a warehouse, or a rate-limited external API to stay under limits and cut per-call overhead.
- **CDC pipelines** — streaming DB change-data-capture into a warehouse in small chunks.

**When to pick it:** you want "feels real-time" without the operational burden of true streaming, and you benefit from bulk I/O.

---

## The one table to remember

| | Batch | Micro-batch | Streaming |
|---|---|---|---|
| **Unit of work** | Everything | Small group | One event |
| **Latency** | Hours/days | Seconds | Milliseconds |
| **Throughput** | Highest | High | Moderate |
| **Complexity** | Low | Medium | High |
| **Late/out-of-order data** | N/A | Some | The whole battle |
| **Sweet spot** | Reports, ETL, payroll | Near-RT dashboards, bulk sinks | Fraud, alerts, bidding |

---

## How to actually choose (decision heuristic)

1. **What's the latency requirement?** Ask "how stale can this data be before it's useless?"
   - Hours/days → **batch**
   - Seconds → **micro-batch**
   - Milliseconds → **streaming**
2. **Is an immediate *action* triggered?** (block a card, fire an alert) → streaming.
3. **Do you benefit from bulk I/O / rate limits?** → lean micro-batch over pure streaming.
4. **Default bias:** start with **batch** (simplest, cheapest, easiest to reason about and debug). Move to micro-batch when someone genuinely needs fresher data. Reach for true streaming only when milliseconds have real dollar value — it's the most expensive to build *and operate*.

**The key insight:** these aren't three rival technologies — they're three points on a single latency-vs-efficiency dial. Batch and streaming are the two extremes; micro-batching is the discretized middle, which is why it dominates real-world "real-time" systems that don't actually need per-event immediacy.

Want me to go one level deeper on any one — e.g. the windowing/late-data problem in streaming, or how Spark's micro-batch engine actually works under the hood?
