# 🌥️ **Google Cloud Platform (GCP) – Comprehensive Study Guide**

This guide covers **Storage, Containers & Kubernetes, GKE, Developing Applications on Google Cloud**, and **Prompt Engineering** based entirely on the notes you provided.

---

# **1. Storage in Google Cloud**

Google Cloud provides several storage options optimized for different workloads.

---

## **1.1 Cloud Storage (Object Storage)**

Google’s scalable object storage service.

### **Storage Classes**

* **Standard:** For hot, frequently accessed data
* **Nearline:** For data accessed ~monthly
* **Coldline:** For data accessed infrequently (quarterly)
* **Archive:** For long-term archival and disaster recovery

### **Auto-Class**

Automatically transitions objects to cost-optimized storage classes based on access patterns.

### **Assessment Question Added**

**Why would a customer consider the Coldline storage class?**
✔ To **save money on storing infrequently accessed data**.

---

## **1.2 Cloud SQL (Managed Relational Databases)**

Supports:

* MySQL
* PostgreSQL
* SQL Server

Fully managed, handles backups, replication, and maintenance.

---

## **1.3 Cloud Spanner (Horizontally Scalable Relational Database)**

Designed for:

* **Global-scale relational workloads**
* **Strong consistency** across regions
* **High performance** (tens of thousands of reads/writes per second)
* **SQL support with joins and secondary indexes**

### **Assessment Question Added**

**Which relational database scales to higher database sizes?**
✔ **Spanner**

---

## **1.4 Firestore (NoSQL Document Database)**

A flexible NoSQL database for:

* Mobile
* Web
* Server applications

Capabilities:

* Automatic **multi-region replication**
* **Strong consistency**
* **Atomic batch operations**
* **True transactions**

---

## **1.5 Bigtable (Wide-Column NoSQL Database)**

Google’s big-data NoSQL service.
Ideal for:

* Time-series data
* Analytical workloads
* Real-time processing

---

# **2. Containers & Kubernetes**

---

## **2.1 Kubernetes Overview**

Kubernetes is an open-source system for:

* Managing containerized workloads
* Orchestrating services
* Scaling microservices
* Performing deployments and rollouts

### **Architecture**

* **Control plane** components manage the cluster
* **Nodes** run the container workloads
* A Kubernetes node ≠ a Google Cloud node (VM), though nodes often run on Compute Engine VMs

---

## **2.2 Pods**

* Smallest deployable unit in Kubernetes
* A Pod = **one or more containers**
* Containers in a Pod start/stop/scale **together**
* Most Pods contain **one container**, but tightly coupled containers can share the same Pod

---

## **2.3 Deployments**

Manages:

* Replica sets of Pods
* Application availability
* Safe rolling updates

Commands:

```
kubectl get pods
kubectl get deployments
kubectl describe deployments
```

---

## **2.4 Services**

Provides:

* Stable IP address
* Load balancing
* Logical grouping of Pods

Pods change IPs, but Services stay stable.

---

## **2.5 Scaling**

```
kubectl scale
```

Autoscaling can be configured based on metrics such as CPU utilization.

---

## **2.6 Declarative Configuration**

Define desired state via YAML files:

```
kubectl apply
```

---

## **2.7 Rolling Updates**

```
kubectl rollout
```

Kubernetes ensures smooth transitions between versions by managing Pod replacement safely.

---

# **3. Google Kubernetes Engine (GKE)**

GKE is Google’s **managed Kubernetes platform**.

---

## **3.1 How GKE Enhances Kubernetes**

* Google manages the entire control plane
* Provides a stable Kubernetes API endpoint
* Automatically handles scaling, health, and maintenance of master components
* Eliminates need to manage your own control-plane VMs

GKE clusters run on **Compute Engine**, benefiting from:

* Compute Engine performance & flexibility
* Google VPC networking features

---

## **3.2 GKE Modes**

### **Autopilot Mode (Recommended)**

GKE manages:

* Node configuration
* Autoscaling
* Auto-upgrades
* Security baselines
* Networking baselines

Delivers:

* Production-optimized environment
* Strong security posture
* High operational efficiency

### **Standard Mode**

You manage:

* Node infrastructure
* Node sizing
* Cluster optimization

Use when fine-grained control is needed.

---

## **3.3 Creating a Cluster**

```
gcloud container clusters create k1
```

Clusters can be customized for:

* Machine types
* Node counts
* Network configurations

---

## **3.4 Advanced GKE Features**

* Cloud load balancing
* Node pools
* Cluster autoscaling
* Node auto-upgrades
* Node auto-repair
* Cloud Logging & Monitoring via Google Cloud Observability

---

# **4. Developing Applications on Google Cloud**

---

## **4.1 Cloud Run**

A **serverless** platform for running **stateless containers** triggered by:

* HTTP requests
* Pub/Sub events

Built on **Knative**, which runs on Kubernetes.

### **Enable Cloud Run**

```
gcloud services enable run.googleapis.com
```

---

## **4.2 Cloud Run Functions**

A lightweight, event-first, asynchronous compute option.

Benefits:

* Small, single-purpose functions
* Event-driven (Pub/Sub, Cloud Storage, etc.)
* Fully serverless
* Auto-scaling
* Integrated with Cloud Logging

### **Assessment: Correct Statements**

Cloud Run functions:
✔ Are a scalable functions-as-a-service platform
✔ Are integrated with Cloud Logging
✔ Can extend cloud services

---

## **4.3 Cloud Build**

Executes steps in **Docker containers** to build application images and push to Artifact Registry.

### **Sample command**

```
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/helloworld
```

---

## **4.4 Cloud Run vs Cloud Run Functions**

**Cloud Run** is best when running a **full-featured containerized application**, such as:

✔ **Hosting a dynamic web application where users upload and share photos**

Cloud Run Functions are for small, event-based tasks like:

* Sending email notifications
* Generating thumbnails
* Processing storage events

---

# **5. Prompt Engineering**

---

## **5.1 Prompting Techniques**

### **Zero-shot prompting**

Model receives only the instruction.

### **One-shot / Few-shot prompting**

Examples are included to teach structure or logic.

### **Role prompting**

Assigns a role (e.g., “You are a cloud architect”).

---

## **5.2 Prompt Structure**

**Preamble + Input**

### **Preamble components**

* **Context**
* **Instruction/Task**
* **Examples** (one-shot/few-shot)

---

## **Example Prompt**

> You're a cloud architect. You want to build a Google Cloud VPC network that can be centrally managed. You also connect to other VPC networks in your company's other regions. You don't want to have many different sets of firewall policies to maintain. What sort of network architecture would you recommend?

Role: Cloud architect
Context: Multi-region networking + centralized management
Task: Recommend an architecture

---

