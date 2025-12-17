# **🌥️ Google Cloud – Identity, IAM, Security & Authentication Guide**

*A ready-reckoner covering IAM, identity, authentication, networking, APIs, OAuth, Firebase Auth, ADC, Workload Identity, Secrets, and relevant lab commands.*

---

# **1. IAM (Identity & Access Management)**

## **1.1 What IAM does**

* **Specifies who can do what** on which resources.
* Identity = *who you are*
* Authorization = *what you’re allowed to do*

## **1.2 IAM Principals (Who can access resources)**

### **1. Google Account (User)**

* Represents an individual user.

### **2. Service Account (Application / workload)**

* Used by applications or VMs to call Google Cloud APIs.
* Authenticated using **private/public RSA key pair**.
* **No password**.
* Private key must NEVER be committed to GitHub.

### **3. Google Group**

* Collection of Google accounts/service accounts.
* **No login credentials** → cannot establish identity.
* Used for applying permissions conveniently.

### **4. Google Workspace Account**

* Group of Google accounts under a company domain (e.g., `company.com`).
* Also cannot authenticate directly.
* Used for centralized permission management.

### **5. Cloud Identity Domain**

* Similar to Workspace but without Workspace apps.
* Also cannot authenticate directly.
* Used to manage users/groups/policies.

**Summary:**
Google Groups, Workspace, and Cloud Identity → **not identities**, but **permission management tools**.

---

# **2. IAM Permissions & Roles**

## **2.1 Permissions**

Format:
**service.resource.verb**
Example:
`pubsub.permissions.consume`

Permissions **cannot** be assigned directly to a user.
You assign **roles**, which contain permissions.

## **2.2 Types of IAM Roles**

### **1. Basic Roles**

* `roles/viewer`, `roles/editor`, `roles/owner`
* **Too broad** → not recommended.

### **2. Predefined Roles**

* Granular access for specific services.
* Created & maintained by Google.
* Examples:

  * `roles/compute.admin`
  * `roles/storage.objectViewer`

### **3. Custom Roles**

* You create them.
* Best for **principle of least privilege**.

**Note:** A user can have **multiple roles**.

---

# **3. Authentication vs Authorization**

## **Authentication = Who you are**

* OAuth tokens more secure than API keys.
* Logging in creates an OAuth token (short-lived).
* Service accounts use key pairs.

## **Authorization = What you can do**

* IAM roles determine allowed actions.

---

# **4. Authenticating Applications**

## **4.1 Application Default Credentials (ADC)**

ADC checks credentials in this order:

1. **`GOOGLE_APPLICATION_CREDENTIALS`** environment variable
2. **User credentials** from `gcloud auth application-default login`
3. **Attached service account** (Compute Engine, Cloud Run, etc.)

---

# **5. Best Authentication Methods Based on Environment**

## **5.1 If running inside Google Cloud**

### **Not on GKE?**

* **Local development:**
  `gcloud auth application-default login`
* **Cloud instance:**
  Attach a **service account** to the VM / Cloud Run / Cloud Functions.

### **On GKE?**

* Use **Workload Identity**

  * Enable it on the cluster.
  * Bind Kubernetes SA → GCP SA.
  * ADC handles access.

## **5.2 Running outside Google Cloud**

### **If federation is possible → Prefer this**

✔ **Workload Identity Federation**

* Exchanges external OIDC token for short-lived Google token.

### **If no federation**

⚠ **Service account key** (least preferred)

* Must secure carefully.

---

# **6. Accessing Resources on Behalf of a User**

## **Option 1: OAuth 2.0**

* Used when app needs user consent.
* Flow:

  1. App redirects to Google
  2. User authenticates + consents
  3. App receives authorization **code**
  4. Code exchanged for **access token + refresh token**

### Sample callback response (OAuth Success)

Contains:

* `code` (authorization code)
* scopes allowed
* user identity details

If user denies consent, no `code` is returned.

⚠ **Client_secret.json must be protected like a password.**

## **Option 2: Identity-Aware Proxy (IAP)**

* Verifies user identity before reaching the app.
* Applies IAM-based access.
* Allows secure access **without a VPN**.

---

# **7. Firebase Authentication**

* Provides authentication using:

  * Passwords
  * Phone numbers
  * Google, Apple, GitHub sign-in
* Ideal for apps you don’t want to build auth for.
* **Can be used outside Google Cloud** (AWS, Azure, on-prem, Vercel, etc.)
* Identity Platform (paid upgrade) adds:

  * SAML
  * OIDC
  * Multi-tenancy

---

# **8. Secret Manager**

Used to store:

* API keys
* Passwords
* Certificates

Example commands:

```
gcloud services enable secretmanager.googleapis.com
gcloud secrets create bookshelf-client-secrets --data-file=$HOME/client_secret.json
tr -dc A-Za-z0-9 </dev/urandom | head -c 20 | gcloud secrets create flask-secret-key --data-file=-
```

---

# **9. VPC & Subnet Concepts**

### Subnet scope is **regional** (not zonal or global).

### ICMP

* Needed for **ping**.
* Removing ICMP firewall rule → ping stops working.

---

# **10. Preemptible VMs**

* Main reason customers choose them:
  ✔ **Reduce cost**

---

# **11. Cloud Storage Family**

* Cloud Storage
* Cloud SQL
* Spanner
* Firestore
* Bigtable

---

# **12. LLM (Large Language Model)**

* Trained on **very large datasets** (sometimes PB-scale).
* Contain **billions of parameters**.

---

# **13. Common Lab Commands**

### Firestore database:

```
gcloud firestore databases create --location=us-east4
```

### Create storage bucket:

```
gcloud storage buckets create gs://bucket-name --location=us-east4 --no-public-access-prevention --uniform-bucket-level-access
```

### Make bucket public:

```
gcloud storage buckets add-iam-policy-binding gs://bucket-name --member=allUsers --role=roles/storage.legacyObjectReader
```

### Download and extract sample code:

```
gcloud storage cp gs://cloud-training/devapps-foundations/code/lab2/bookshelf.zip ~
unzip ~/bookshelf.zip -d ~
rm ~/bookshelf.zip
```

### Install dependencies:

```
pip3 install -r ~/bookshelf/requirements.txt --user
```

### Run dev server:

```
cd ~/bookshelf; ~/.local/bin/gunicorn -b :8080 main:app
```

---

# **14. Checkpoint Questions (from your notes)**

### **1️⃣ Access internal app without VPN**

✔ **Use Identity-Aware Proxy (IAP)**

* Provides application-level access without VPN.
* Authenticates + authorizes users before request reaches app.

---

### **2️⃣ App requires user login; don’t want custom auth**

✔ **Use Firebase Authentication**

* Provides secure login, passwordless auth, federated identity.
* No need to manage passwords.

---

### **3️⃣ Label entities in video before storage**

✔ **Use Video Intelligence API**

