# 🌥️ **Google Cloud: Application Development & Storage Concepts Refresher Guide**

This guide summarizes key concepts, best practices, tools, and services needed to design, build, deploy, and operate cloud-native applications on Google Cloud.
Use it for revision before interviews, exams, or hands-on work.

---

# 1️⃣ **Designing Applications for the Cloud**

Applications running on the cloud must support:

### ✔ **Global Reach**

Built to serve users across the world efficiently.

### ✔ **Scalability & High Availability**

Automatic scaling and redundancy ensure apps handle varying workloads.

### ✔ **Security**

Strong identity, access, and data controls.

---

## **Best Practices for Cloud-Native Apps**

### 🔹 **1. Store your code in version control**

Use Git or similar systems for collaboration and rollback.

### 🔹 **2. Don’t store external dependencies in your repo**

Declare dependencies and let package managers install them.

### 🔹 **3. Use environment variables for configuration**

Avoid hardcoding sensitive or environment-specific values.

### 🔹 **4. Consider microservices architecture**

Smaller components are easier to scale and update independently.

### 🔹 **5. Keep UI responsive**

Perform heavy backend tasks **asynchronously** using:

* Event-driven patterns
* Cloud Pub/Sub
* Cloud Tasks

### 🔹 **6. Loosely-coupled runtime design**

Use messaging systems like **Pub/Sub** instead of direct service-to-service calls.

### 🔹 **7. Implement stateless components**

Statelessness allows effortless scaling.

* Cloud Run services should not store shared state.
* Persist application state in external storage (Firestore, SQL, Bigtable, etc.).

### 🔹 **8. Error handling**

* **Transient errors** → Retry using **exponential backoff**.

  * Cloud Client Libraries automatically perform safe retries.
* **Long-lasting failures** → Implement a **circuit breaker** to prevent cascading failures.

---

# 2️⃣ **Caching & Content Delivery**

### 🔹 Check cache first

Apps should consult cache before making expensive calls.

### 🔹 **Memorystore**

Google’s managed Redis/Memcached service for ultra-low latency data access.

### 🔹 **Cloud CDN**

Delivers cached web content using Google’s global edge network.

### 🔹 **Serving static content**

Static files can be served from:

* Cloud Storage
* Cloud Run services/functions
* Compute Engine instance groups

### 🔹 **Apigee**

A full API management platform for building, securing, analyzing APIs.

---

# 3️⃣ **Development Approaches in Google Cloud**

## **A. Cloud APIs & Cloud SDK**

* Cloud APIs = programmatic interface to GCP services.
* Cloud SDK = CLI tools + client libraries used behind-the-scenes to call Cloud APIs.

## **B. Google Cloud CLI (gcloud)**

Command-line tool to manage resources.

Examples:

* `gcloud compute instances list`
* Install Kubernetes CLI: `gcloud components install kubectl`
* Update gcloud: `gcloud components update`
* Manage storage: `gcloud storage cp …`
* BigQuery CLI: `bq`

**gsutil** still exists but `gcloud storage` is the newer, recommended interface.

---

# 4️⃣ **Cloud Client Libraries**

These are language-specific libraries for interacting with Google Cloud services.

### ✔ Supports all languages used on Google Cloud

(Python, Java, Go, Node.js, C#, Ruby, PHP, etc.)

### ✔ Handles:

* Authentication
* Retries & exponential backoff
* Paging
* Errors
* IAM integration

### ✔ Follows natural idioms of the language

E.g., Pythonic conventions for Python, builders/promises for Java & Node.js.

---

# 5️⃣ **Cloud Shell & Cloud Code**

## **Cloud Shell**

* A free browser-accessible VM.
* Pre-installed Cloud SDK & tools (gcloud, kubectl, bq).
* Comes with persistent `/home` storage.
* Automatically authenticated to user’s Google Cloud project.

## **Cloud Code**

A set of IDE extensions for:

* **VS Code**
* **IntelliJ**
* **Cloud Shell Editor**

### Features

* Simplifies Cloud Run and Kubernetes development.
* YAML authoring assistance (autocomplete, inline docs).
* Integrated emulators for local dev:

  * Firestore
  * Spanner
  * Pub/Sub
  * Cloud Functions (via frameworks)
* Integrates with **Secret Manager** for secure secret handling.

---

# 6️⃣ **Google Cloud Storage & Database Options**

## **1. Cloud Storage**

* Object storage; HTTP-based access.
* Max object size: **5 TB**.
* Ideal for images, videos, backups, static sites.

## **2. Firestore**

* NoSQL, document-oriented DB.
* Stores hierarchical collections of documents.
* Best for mobile/web apps needing real-time sync.

## **3. Bigtable**

* High-throughput NoSQL wide-column database.
* Excellent for analytical or time-series workloads.

## **4. Cloud SQL**

* Managed MySQL / Postgres / SQL Server.
* Automatic backups, replication, failover.
* Ideal for OLTP workloads.

## **5. AlloyDB**

* PostgreSQL-compatible, high-performance database.
* Columnar engine may give **up to 100× faster analytics**.

## **6. Spanner**

* Horizontally scalable, globally consistent relational database.
* 99.999% availability SLA.
* Mission-critical distributed SQL workloads.

## **7. BigQuery**

* Serverless data warehouse.
* Scans TB in seconds, PB in minutes.
* Supports standard SQL.

## **8. Memorystore**

* Managed Redis/Memcached for caching.

---

# 7️⃣ **Lab Summary (From Notes)**

**Build a simple full-stack cloud app:**

1. Create a Python Flask web application.
2. Use **Firestore** to store application data.
3. Use **Cloud Storage** to store images.

---

# 8️⃣ **Quick Learning Checks (All Added)**

### ✔ Transient errors → **Retry with exponential backoff.**

(Cloud Client Libraries handle this automatically.)

### ✔ Long-lasting failures → **Use circuit breaker.**

---

### **Cloud Code – True Statements**

* Cloud Code integrates with **Secret Manager**.
* Cloud Code works with **Cloud Run and Kubernetes**.

---

### **Google Cloud Client Libraries – True Statements**

* Provided in all languages used on Google Cloud.
* Handle retries, authentication, paging.
* Follow natural language conventions and coding styles.

---
