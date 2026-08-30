# Your Kafka learning roadmap

You've got the mental model. Now the goal is to **build things with your hands** — Kafka clicks through doing, not reading. Here's a staged path from zero to job-ready.

---

## Stage 1 — Get Kafka running locally (½ day)

Don't install Kafka manually. Use Docker.

```bash
docker run -d --name=kafka -p 9092:9092 apache/kafka:latest
```

Then learn the **CLI tools** that ship with Kafka — they make the abstract concepts concrete:

```bash
# create a topic with 4 partitions
kafka-topics.sh --create --topic orders --partitions 4 --bootstrap-server localhost:9092

# produce messages by typing them
kafka-console-producer.sh --topic orders --bootstrap-server localhost:9092

# consume them in another terminal
kafka-console-consumer.sh --topic orders --from-beginning --bootstrap-server localhost:9092
```

**Goal:** watch a message you type appear in the consumer. See partitions and offsets with `kafka-topics.sh --describe` and `kafka-consumer-groups.sh --describe`.

---

## Stage 2 — Raw Java clients (1–2 days)

Write the plain `kafka-clients` producer + consumer from my earlier message. This forces you to understand `poll()`, offsets, and manual commits — the machinery Spring later hides.

**Experiments that build intuition:**
- Send messages **with a key** vs without → watch which partition they land in.
- Start **two consumers in the same group** → watch partitions split between them.
- Start a consumer in a **different group** → watch it get *all* messages independently.
- Kill a consumer mid-run → watch **rebalancing** reassign its partitions.

> These four experiments teach you more than any article.

---

## Stage 3 — Spring Kafka (2–3 days) — this is the job skill

Rebuild Stage 2 with Spring Boot and `@KafkaListener`. Then add the things real projects need:

- **JSON serialization** — send actual objects, not strings.
- **Manual acknowledgment** (`AckMode.MANUAL_IMMEDIATE`) — control *when* the bookmark advances.
- **Error handling** — `DefaultErrorHandler` with retry + backoff.
- **Dead Letter Topic (DLT)** — route poison messages to `orders.DLT` instead of blocking.
- **Idempotency** — make your consumer safe to run a message twice (because at-least-once means you will).

**Project idea:** an order service. Producer publishes orders; consumer processes them, writes to a DB, and dead-letters malformed ones.

---

## Stage 4 — Production concepts (ongoing)

These separate "I made it work" from "I understand it":

| Topic | Why it matters |
|---|---|
| **Replication factor & ISR** | How Kafka survives a broker dying without losing data |
| **`acks=all` vs `acks=1`** | Producer durability vs speed tradeoff |
| **Consumer lag** | The #1 metric you'll monitor in prod ("are we falling behind?") |
| **Schema Registry + Avro** | How teams evolve message formats without breaking consumers |
| **Retention & compaction** | How long messages live; log compaction for "latest value per key" |
| **Partitioning strategy** | Choosing keys so load is even *and* ordering holds |

---

## Stage 5 — The bigger ecosystem (when ready)

- **Kafka Streams** — transform topics into topics in Java (joins, aggregations, windowing). The natural next step for Java devs.
- **Kafka Connect** — config-only integration to databases and systems, no code.
- **Transactions / exactly-once semantics** — advanced; only after everything above is solid.

---

## How to sequence it

```
Week 1:  Stage 1 + 2   → CLI + raw clients, do the 4 experiments
Week 2:  Stage 3        → Spring Kafka order service with DLT + retries
Week 3+: Stage 4        → pick concepts as your real project demands them
Later:   Stage 5        → Streams when you need transformations
```

**Rule of thumb:** don't learn Stage 4/5 topics in the abstract. Learn each one *when a project forces the question* ("why did we lose a message?" → go learn `acks`). That's how it sticks.

---

## Best resources

- **Confluent Developer** (developer.confluent.io) — free, hands-on, genuinely the best Kafka learning site.
- **Official Apache Kafka docs** — the "Design" and "Implementation" sections are worth a slow read once you have context.
- **Spring for Apache Kafka reference docs** — for Stage 3 onward.

---

Want me to spin up a concrete **Stage 3 starter project** for you — a runnable Spring Boot order service with producer, `@KafkaListener` consumer, JSON, retries, and a dead-letter topic — so you have working code to experiment on? I can scaffold the whole thing.

Yes — and the good news is Kafka has unusually good **free** learning resources. Here's where to go, mapped to each stage.

---

## 🥇 The best one: Confluent Developer
**developer.confluent.io**

This is the single best free Kafka resource, made by the company founded by Kafka's original creators. Everything is free (you just make a free account for some hands-on parts).

- **Courses** (`developer.confluent.io/courses`) — video courses with hands-on exercises:
  - *"Apache Kafka 101"* → perfect for **Stage 1** (concepts + running Kafka + CLI).
  - *"Kafka Producers and Consumers (Hands On)"* → **Stage 2** (raw clients).
  - *"Spring Framework and Apache Kafka"* → **Stage 3**.
  - *"Kafka Streams 101"* → **Stage 5**.
- **Tutorials** (`developer.confluent.io/tutorials`) — copy-paste recipes ("how do I do X").

Start here. It covers Stages 1–5 end to end.

---

## 🥈 Official Apache Kafka docs
**kafka.apache.org/documentation**

- **Quickstart** (`kafka.apache.org/quickstart`) → exactly your **Stage 1** — download, start a broker, create a topic, produce/consume from the CLI. Follow it step by step.
- The **Design** section is a great slow-read once you have context (Stage 4 concepts like replication, ISR, retention).

---

## 🥉 Spring Kafka official docs — for Stage 3
**docs.spring.io/spring-kafka/reference**

The reference guide with `@KafkaListener`, error handlers, and dead-letter topics. Pair it with the free Spring guide at **spring.io/guides** (search "Messaging with Kafka").

---

## For hands-on practice without any local setup

- **Confluent Cloud** — free tier with credits, gives you a real Kafka cluster in the browser (no Docker needed). Good if local setup annoys you.
- **GitHub: `confluentinc/examples`** — free runnable sample projects for Stages 2–5.

---

## Free video (if you prefer watching)

- **freeCodeCamp** on YouTube has a full free "Apache Kafka Crash Course / Full Course" — good for Stages 1–3.
- **Confluent's own YouTube channel** — short, focused explainers.

---

## Suggested path

```
Stage 1  →  Confluent "Kafka 101" course  +  Apache Kafka Quickstart
Stage 2  →  Confluent "Producers & Consumers (Hands On)"
Stage 3  →  Confluent "Spring + Kafka"  +  Spring Kafka docs
Stage 4  →  Apache Kafka docs "Design" section (as questions come up)
Stage 5  →  Confluent "Kafka Streams 101"
```

If I had to pick **one** to start today: create a free account on **developer.confluent.io** and do the *Kafka 101* course while following the *Apache Kafka Quickstart* in a terminal alongside it. That combo covers your Stage 1 completely.

Want me to still scaffold that **Stage 3 Spring Boot starter project** locally so you have working code to poke at while you go through the courses?
