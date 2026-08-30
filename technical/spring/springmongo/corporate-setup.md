Refer `Dockerfile-corp` in repo for actual sample file.
Here’s a concise summary of what made your **Dockerfile work** successfully, focused on the trust and configuration parts 👇
---

## ✅ **1️⃣ Installing system CA certificates**

In both stages (the **Maven build** and the **runtime JRE**):

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates
# or on Alpine:
RUN apk add --no-cache ca-certificates
```

This ensures each image has the base OS certificate store so `update-ca-certificates` works properly.

---

## ✅ **2️⃣ Copying your organization CA `.crt` files**

You provided two separate, single-cert files (`org1.crt` and `org2.crt`).
These were copied into the system’s trusted certificate location:

```dockerfile
COPY org1.crt /usr/local/share/ca-certificates/organization-root.crt
COPY org2.crt /usr/local/share/ca-certificates/organization-intermediate.crt
RUN update-ca-certificates
```

**Why this matters:**
Each `.crt` is in PEM format (one certificate per file).
Placing them under `/usr/local/share/ca-certificates/` and running `update-ca-certificates` adds them into the OS trust store (`/etc/ssl/certs/`), which tools like `curl` and `apt` use for TLS.

---

## ✅ **3️⃣ Importing into Java’s truststore**

Since Java maintains its *own* certificate truststore (`$JAVA_HOME/lib/security/cacerts`), we also imported the same certs there, for Maven and your app’s HTTPS calls:

```dockerfile
RUN for f in /usr/local/share/ca-certificates/organization-*.crt; do \
      echo "Importing $f into Java cacerts"; \
      keytool -importcert -noprompt -storepass changeit \
        -alias "$(basename "$f" .crt)" \
        -file "$f" \
        -keystore "${JAVA_HOME}/lib/security/cacerts" || true; \
    done
```

**Why:**
This ensures that:

* Maven (during dependency downloads)
* and your Spring Boot app (when making outbound HTTPS calls)
  both trust internal organization endpoints (Artifactory, proxy, APIs, etc.).

We applied this block **in both stages** — once in the **build stage** and again in the **runtime stage** — since each has its own JRE installation.

---

## ✅ **4️⃣ Copying a safe `settings.xml`**

Because your Maven `settings.xml` contains only mirror and proxy definitions (no credentials), we safely baked it into the image so Maven can automatically use corporate repositories:

```dockerfile
COPY settings.xml /root/.m2/settings.xml
```

**Why:**
This ensures Maven resolves dependencies through your internal mirrors (e.g., `https://artifactory.organization.com/...`) without needing manual config on every build.

---

## ✅ **5️⃣ Final result**

When the container builds and runs:

* The OS and Java both trust organization’s root and intermediate CAs.
* Maven successfully connects to your internal repository over HTTPS.
* The Spring Boot app, when deployed, can make outbound HTTPS calls without PKIX errors.
* Everything builds cleanly behind your corporate firewall.

---

### 🔍 summary of key improvements

| Step                               | Purpose                                       |
| ---------------------------------- | --------------------------------------------- |
| `COPY org*.crt`                   | Bring in trusted CA files                     |
| `update-ca-certificates`           | Add them to OS trust store                    |
| `keytool -importcert` loop         | Add them to Java’s truststore                 |
| `COPY settings.xml`                | Configure Maven for internal mirrors/proxies  |
| Repeated in build + runtime stages | Ensures both Maven and app trust the same CAs |

---

You now have a fully self-contained, corporate-network-safe image chain — Maven builds and your Spring Boot runtime both operate behind the organization firewall without any PKIX or certificate errors.
