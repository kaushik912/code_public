# ⭐ GCP Monitoring & Logging – Ready-Reckoner Guide

---

# 1. Google Cloud Observability — What It Includes

Google Cloud Observability provides a unified pane for:

* **Cloud Monitoring** → metrics, dashboards, uptime checks, alerts
* **Cloud Logging** → application + system logs, log-based metrics
* **Error Reporting** → exception aggregation & notifications
* **Cloud Trace** → distributed tracing & latency insights
* **Cloud Profiler** → CPU & memory profiling in production

These tools work across **Google Cloud, AWS, on-prem, hybrid** environments.


---

# 2. The Four Golden Signals (SRE Concept)

These are the minimum metrics every production system must monitor.

* **Latency** → Time to serve a request
* **Traffic** → How much demand is placed on system (e.g., RPS)
* **Errors** → Failed requests (HTTP 500, incorrect response, policy errors)
* **Saturation** → How “full” or constrained a system is (CPU, memory, threads)

👉 Systems degrade *before* 100% usage → set realistic targets


---

# 3. Cloud Logging

Cloud Logging is a **real-time log ingestion + analytics** platform.

### Why Use Cloud Logging?

* Troubleshoot issues
* Analyze application performance
* Create log-based metrics
* Trigger alerts from logs


### Logging in Different Environments

* **Compute Engine** → Install **Ops Agent** (replaces old logging/monitoring agents)

  * Collects system + application logs
  * Collects system metrics (CPU, disk, memory, network)
  * Supports third-party apps like Tomcat, Apache, nginx
  * Based on **Fluent Bit** + **OpenTelemetry Collector**


* **Cloud Run / Cloud Functions**

  * Write to **stdout / stderr**, logs auto-shipped to Cloud Logging
  * Text logs → `textPayload`
  * Structured JSON logs → `jsonPayload`
  * Structured logs preferred → can filter/search by fields


* **GKE**

  * Enable **Observability** integration
  * Logs automatically exported to Cloud Logging
  * Cluster logs themselves are ephemeral → must export if retention needed


### Structured Logging Example

```js
console.log(JSON.stringify({
  severity: "NOTICE",
  message: "Inventory system rebooted",
  component: "inventory-tablet-service",
  "logging.googleapis.com/labels": {
    appid: "inventory",
    contact: "commerce@example.org"
  }
}));
```



---

# 4. Metrics & Log-Based Metrics

### Metrics Sources

* System metrics (CPU, memory)
* Platform metrics (Cloud Run, GKE, Load Balancer)
* Log-based metrics (count certain patterns in logs)
* Prometheus metrics


### Log-Based Metrics Use Cases

* Count 500 errors
* Count failed login attempts
* Measure frequency of specific log patterns

---

# 5. Prometheus & Managed Prometheus

### Why Prometheus?

* Standard for Kubernetes monitoring
* Stores **time-series metrics**
* Powerful PromQL language


### Managed Prometheus Benefits

* Fully managed & horizontally scalable
* Multi-cloud, cross-project
* Uses Cloud Monitoring’s backend
* Supports PromQL + Cloud Monitoring metrics


Data collectors supported:

* Managed collector (recommended for GKE)
* Self-deployed Prometheus
* OpenTelemetry collector
* Ops Agent


---

# 6. Error Reporting

Error Reporting aggregates & analyzes application crashes.

### Why Use It?

* Real-time exception monitoring
* Intelligent error grouping
* Email / mobile alerts
* Stack trace exploration


### Environment Requirements

* **Cloud Run** → automatically enabled
* **GCE** → VM Service Account needs `roles/errorreporting.writer`
* **GKE** → cluster needs **cloud-platform** scope


### Error Event (Your Note)

* Error events are reported **asynchronously**, allowing code to continue


### Node.js Example

```js
const { ErrorReporting } = require('@google-cloud/error-reporting');
const errors = new ErrorReporting();
const event = errors.event();

event.setMessage("My error message");
event.setUser("user@example.com");

errors.report(event, () => console.log("Done reporting error!"));
```



---

# 7. Cloud Trace (Distributed Tracing)

Used to analyze **latency** across services.

### Key Concepts

* Automatically captures HTTP latency for Cloud Run
* Instrument using OpenTelemetry for detailed spans
* Daily performance comparison reports


### Traces & Spans

* **Trace** = time to complete an entire request
* **Span** = time for a sub-operation


Trace Explorer:

* Scatter plot of requests
* Click any request → explore spans + timings


---

# 8. Cloud Profiler

Profiler continuously samples production workloads.

### Why Use Cloud Profiler?

* Low overhead (statistical sampling)
* CPU and memory hotspot detection
* Links resource usage to source code lines


Used to reduce:

* Memory leaks
* CPU bottlenecks
* Expensive code paths

---

# 9. Lab Summary — Cloud Run + Logging + Error Reporting

### Steps Performed

### 1. Create Artifact Registry

```sh
gcloud artifacts repositories create app-repo \
  --repository-format=docker \
  --location=us-west1
```

### 2. Build & Push using Buildpacks

```sh
gcloud builds submit \
  --pack image=us-west1-docker.pkg.dev/${PROJECT}/app-repo/bookshelf \
  ~/bookshelf
```

### 3. Deploy to Cloud Run

```sh
gcloud run deploy bookshelf \
  --image=us-west1-docker.pkg.dev/${PROJECT}/app-repo/bookshelf \
  --region=us-west1 \
  --allow-unauthenticated \
  --update-env-vars=GOOGLE_CLOUD_PROJECT=${PROJECT}
```

### 4. Fix Permission Error

Cloud Run uses **Compute Engine default SA**, which lacked permissions.

Create new SA:

```sh
gcloud iam service-accounts create bookshelf-run-sa
```

Assign roles:

```sh
roles/secretmanager.secretAccessor
roles/cloudtranslate.user
roles/datastore.user
roles/storage.objectUser
roles/errorreporting.writer
```

Deploy with SA:

```sh
--service-account=bookshelf-run-sa@${PROJECT}.iam.gserviceaccount.com
```

### 5. OAuth Redirect Mismatch

You updated redirect URI using:

```sh
https://bookshelf-<PROJECT_NUMBER>.us-west1.run.app/oauth2callback
```

---

# 10. Quick Memory Boost — Interview-Ready Points

### Difference between Logging & Monitoring

* Logging: event history
* Monitoring: numeric signals + alerts

### Cloud Run Logging

* Only accepts **HTTP-based protocols** (incl. gRPC via HTTP/2)

### Metrics Storage

* Prometheus → time-series, open source
* Cloud Monitoring → managed metrics platform

### Ops Agent vs Legacy Agents

* Ops Agent = unified logging + metrics
* Faster, recommended

### SRE Golden Signals

* Foundation for production monitoring

### Trace vs Profiler

* Trace → request latency timeline
* Profiler → CPU/memory hotspots

---