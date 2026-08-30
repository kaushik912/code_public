# 🌥️ **Google Cloud Platform (GCP) — Concepts Refresher Guide**

A clean, organized guide based on all your notes.

---

# **1. GCP Resource Hierarchy**

Google Cloud resources follow a **strict hierarchical structure**:

```
Organization → Folder → Project → Resources
```

### **Key Points**

* **Organization** is the root node (usually tied to a company domain).
* **Folders** help group projects and apply policies uniformly.
* **Projects** are the main container for resources like VMs, storage, APIs, billing.
* **Resources** live *inside projects* (VMs, storage buckets, networks, service accounts, etc.).

### **Folders**

* Used mainly to **apply IAM and organization policies** at scale.
* Custom roles **cannot** be defined at the folder level (only at **project** or **organization** level).

### **Service Accounts**

* Service accounts are **resources**, so IAM permissions control:

  * Who can create them
  * Who can view them
  * Who can manage/rotate keys
  * Who can impersonate them

---

# **2. Ways to Interact with Google Cloud**

Four primary interfaces:

1. **Google Cloud Console (UI)**
2. **Cloud SDK**
3. **Cloud APIs**
4. **Google Cloud Mobile App**

### **Cloud SDK vs Cloud Shell**

* **Cloud SDK**: Local CLI tools (`gcloud`, `gsutil`, `bq`, etc.)
* **Cloud Shell**:

  * A **Debian-based ephemeral VM** provided by Google
  * Fully authenticated
  * Preinstalled tools (gcloud + others)
  * Accessible directly from the browser

---

# **3. Enabling Services and APIs**

* Services and APIs are enabled **per project**.
* They cannot be enabled at the **organization** or **folder** level.

---

# **4. VPC Networks (Virtual Private Cloud)**

A **VPC** is a **secure, isolated, private cloud environment** within the Google Cloud public infrastructure.

### **VPC Firewall**

* Global, distributed firewall.
* Firewall rules can be applied using **network tags**.

  * Example: Tag all VMs with `WEB`, then allow inbound traffic on **80/443** to all VMs with that tag.

### **ICMP**

* ICMP rules allow **ping**.
* Removing ICMP allow rules → **ping will stop working**.

---

# **5. Default VPC Network**

When you create a new project:

* Google automatically creates a **default VPC**.
* It includes:

  * One **subnet per region** (auto mode)
  * Default firewall rules (allow SSH, RDP, ICMP)

### Deleting a VPC

* Removes all:

  * Subnets
  * Firewall rules
  * Routes
* Because these cannot exist without the VPC.

---

# **6. Regions, Zones, and Subnets**

### **Subnets have *regional* scope.**

* A subnet lives in **one region**, but covers **all zones** in that region.

### VM Placement

* When creating a VM:

  * Your **region/zone selection** determines the **subnet**.
  * VM receives an internal IP from that subnet’s **CIDR range**.

### Example Explanation

A VPC **vpc1** has subnets in:

* **asia-east1**
* **us-east1**

If you create three VMs in **asia-east1-a**, **asia-east1-b**, **asia-east1-c** within the same subnet:

* They are **neighbors** on the same subnet
* Even though they are in **different zones**

Because **subnets span zones**.

---

# **7. Cloud Marketplace**

A quick way to get started:

* Offers ready-to-deploy solutions from Google and third-party vendors.
* No need to install software or configure VMs manually.
* Useful for deploying production-ready stacks in minutes.

---

# **8. Interconnect Options & SLA Availability**

Only **Dedicated Interconnect** provides a **Service Level Agreement**.

| Interconnect Option        | SLA Available? | Notes                                   |
| -------------------------- | -------------- | --------------------------------------- |
| **Dedicated Interconnect** | ✅ Yes          | Private physical link; enterprise-grade |
| Carrier Peering            | ❌ No           | ISP intermediary                        |
| Direct Peering             | ❌ No           | Public peering, no SLA                  |
| Standard Network Tier      | ❌ No           | Best-effort internet routing            |

---

# **9. Preemptible VMs**

### **Main reason customers choose them:**

✔ **Cost reduction**

* Up to **70–90% cheaper** than standard VMs.
* Can be terminated anytime and must stop after **24 hours**.
* Not chosen for OS licensing reasons.

---

# **10. Storage Options in Google Cloud**

Google Cloud offers several managed storage services:

| Service           | Type              | Best For                                         |
| ----------------- | ----------------- | ------------------------------------------------ |
| **Cloud Storage** | Object storage    | Unstructured data, backups                       |
| **Cloud SQL**     | Relational        | Traditional apps (MySQL, PostgreSQL, SQL Server) |
| **Cloud Spanner** | Global relational | Large-scale, strongly consistent workloads       |
| **Firestore**     | NoSQL document    | App data, mobile/web backends                    |
| **Bigtable**      | NoSQL wide-column | Analytics, time-series, massive datasets         |

---

# ============================================================

# 📘 **Appendix: Subnet Examples & How to Understand Them**

# ============================================================

This section contains conceptual explanations only — separate from main GCP notes.

---

# **1. Understanding CIDR: `/24` Example**

`10.1.0.0/24` means:

* First **24 bits** = network
* Last **8 bits** = host addresses (`2^8 = 256` total IPs)

Range:

```
10.1.0.0 → 10.1.0.255
```

Google reserves 5, leaving **251 usable IPs**.

---

# **2. Extended Subnet Example (Asia & Europe)**

VPC range:

```
10.1.0.0/16
```

Subnets:

* Asia-east1 → `10.1.0.0/24`
* Europe-west1 → `10.1.1.0/24`

Asia VMs (10.1.0.x) can talk directly → same subnet.
US VMs (10.1.1.x) are in another subnet → not neighbors.

---

# **3. Understanding Big Networks: `/9` Example**

`10.128.0.0/9`

* `/9` → first **9 bits** fixed
* Leaves **23 bits** for hosts → `2^23 = 8,388,608` IPs

Why it starts at `10.128.x.x`?

* 128 in binary = `10000000`
* `/9` fixes the **first bit** of the second octet → must start with `1xxxxxxx` (128–255)

Range:

```
10.128.0.0 → 10.255.255.255
```

---

# **4. Understanding `/20` With Example**

Subnet:

```
10.140.0.0/20
```

Meaning:

* `/20` → first **20 bits** network
* Leaves **12 bits** → `2^12 = 4096` IPs

Block size in 3rd octet = 16 (because 32 − 20 = 12 bits → 4 bits in 3rd octet variable).

Range:

```
10.140.0.0 → 10.140.15.255
```

VM IP example:

```
10.140.0.2
```

This is one of the first usable addresses in the subnet.

---

