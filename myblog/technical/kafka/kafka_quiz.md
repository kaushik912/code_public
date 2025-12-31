# 📘 Kafka Notes

## 1. Which of these is **not** a Kafka data function?

**A.** Processing
**B.** Storage
**C.** Tracking data consumption
**D.** Collection

✅ **Correct Answer:** **A. Processing**

**Explanation:**
Apache Kafka’s core data functions include:

* **Collection** – ingesting data from producers
* **Storage** – durably storing records in topics
* **Tracking data consumption** – managing consumer offsets

Kafka itself **does not process data**. Data processing is handled by tools built on top of Kafka, such as **Kafka Streams**, **ksqlDB**, or **Apache Spark**.

---

## 2. Which of these is an important use case for Kafka?

**A.** Event sourcing
**B.** Graph database
**C.** Video player
**D.** State management

✅ **Correct Answer:** **A. Event sourcing**

**Explanation:**
Kafka is commonly used for **event sourcing**, where every state change in a system is recorded as an immutable event in a Kafka topic. These events can be replayed to rebuild state or drive downstream systems.

**Why the others are incorrect:**

* **Graph database** ❌ – Kafka is not a database
* **Video player** ❌ – Kafka does not handle media playback
* **State management** ❌ – Kafka stores events, not application state


