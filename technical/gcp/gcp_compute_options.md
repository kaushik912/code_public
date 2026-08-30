# **Compute Options in Google Cloud – Refresher Guide**

## **1. Compute Engine**

* Provides **virtual machines (VMs)** on Google Cloud.
* Offers full control over machine types, OS, networking, and storage.
* Best for workloads that require fine-grained control over infrastructure.

---

## **2. Google Kubernetes Engine (GKE)**

* A **managed Kubernetes service** for running containerized applications.
* Automatically manages node pools, scaling, upgrades, and cluster health.
* Primarily for **containers**, but VMs still back the clusters under the hood.

---

## **3. Cloud Run**

* A **fully serverless** platform for running containerized applications.
* **Infrastructure is fully abstracted**—no servers or clusters to manage.
* **Billing is per-request and per-compute time**: you pay only when the service is running.
* Deploy with a **single command**:
  `gcloud run deploy`
* Supports multiple **deployment types**: containers, source code, functions, and continuous deployments from repositories.

---

# **Cloud Run Deployment Types**

### **1. Container**

* Deploy an existing container image.
* Supported image repositories:

  * **Docker Hub**
  * **Artifact Registry**

### **2. Source Code**

* Deploy your **source code directly**, without building an image yourself.
* Cloud Run automatically:

  * Builds the source code → container image
  * Uses **buildpacks** to create secure, cloud-agnostic images.

### **3. Functions**

* Lets you deploy single-purpose functions instead of whole apps.
* Ideal for:

  * Event-driven microservices
  * Lightweight workloads

### **4. Repository Deployment**

* Enables **continuous deployment** from a GitHub repository.
* Automatically builds and updates Cloud Run services when code changes.

---

# **Cloud Run Deployment Workflow**

1. **Write your application code.**
2. **Build** the application into a **container image** (manually or automatically).
3. **Deploy** the container to Cloud Run.

---

# **Cloud Run Jobs**

* A **serverless execution environment** for running **one-off or batch tasks**.
* Unlike Cloud Run services, jobs **do not listen for HTTP requests**.
* Useful for:

  * Data processing
  * Scheduled tasks
  * Background jobs
* Can be orchestrated with **Cloud Scheduler** for periodic execution.

---


