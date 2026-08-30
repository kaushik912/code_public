# 🧩 **Docker Compose Volumes — Complete Guide (todo-service Example)**

NOTE: This is specific to Colima which I used in my corp setup. But steps would be similar for other runtimes.

## 1️⃣ Your setup

In your `docker-compose.yml`:

```yaml
services:
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
volumes:
  mongo-data:
```

➡️ This tells Docker Compose to **mount a persistent volume** named `mongo-data` to `/data/db` inside the MongoDB container — where MongoDB stores all its data.

---

## 2️⃣ How Docker names your volume

Compose automatically prefixes the volume with your **project name** (default = folder name containing the `docker-compose.yml`).

So in your case, the actual volume name becomes:

```
todo-service_mongo-data
```

---

## 3️⃣ Where the data is stored (Colima on macOS)

Since Docker runs inside **Colima’s Linux VM**, all volumes are stored there under:

```
/var/lib/docker/volumes/
```

Your MongoDB files live at:

```
/var/lib/docker/volumes/todo-service_mongo-data/_data/
```

You can view them from inside the Colima VM:

```bash
colima ssh
sudo ls /var/lib/docker/volumes/todo-service_mongo-data/_data
```

This directory contains Mongo’s actual database files (e.g. `.wt` collection files, `journal/`, `diagnostic.data/`, etc.).

---

## 4️⃣ Persistence behavior

| Command                  | What happens                               | Data survives? |
| ------------------------ | ------------------------------------------ | -------------- |
| `docker compose stop`    | Stops containers                           | ✅ Yes          |
| `docker compose down`    | Removes containers & network, keeps volume | ✅ Yes          |
| `docker compose down -v` | Removes containers, network **and volume** | ❌ No           |
| `colima delete`          | Deletes VM (and all volumes)               | ❌ No           |

So your MongoDB data persists as long as you don’t delete the volume or the Colima VM.

---

## 5️⃣ Mounting the same volume automatically

Each time you run:

```bash
docker compose up -d
```

Compose automatically mounts the `mongo-data` volume again — no manual setup required.
You only lose it if you explicitly remove it with `down -v`.

If you want to protect an existing volume (so Compose never recreates it), declare it as **external**:

```yaml
volumes:
  mongo-data:
    external: true
```

Then create it once:

```bash
docker volume create mongo-data
```

---

## 6️⃣ Using your own path instead (bind mount)

If you want MongoDB data to live on your Mac (outside of Colima’s VM), use a **bind mount**:

```yaml
services:
  mongo:
    image: mongo:7
    volumes:
      - ./mongo-data:/data/db
```

* Docker will now use the `mongo-data` folder in your project directory.
* You can browse it in Finder or VS Code.
* Slightly slower than named volumes (since it crosses the host/VM boundary), but great for dev and backup visibility.

---

## 7️⃣ Managing and inspecting volumes

List all Docker volumes:

```bash
docker volume ls
```

Inspect details about your `todo-service` volume:

```bash
docker volume inspect todo-service_mongo-data
```

Sample output:

```json
[
  {
    "CreatedAt": "2025-10-24T08:22:13Z",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/todo-service_mongo-data/_data",
    "Name": "todo-service_mongo-data",
    "Scope": "local"
  }
]
```

---

## ✅ **Summary**

| Concept                | Example                                                              | Purpose                                   |
| ---------------------- | -------------------------------------------------------------------- | ----------------------------------------- |
| **Named volume**       | `mongo-data` → becomes `todo-service_mongo-data`                     | Persistent data managed by Docker         |
| **Data path (Colima)** | `/var/lib/docker/volumes/todo-service_mongo-data/_data`              | Where MongoDB actually stores data        |
| **Persistence**        | Survives restarts, removed only with `down -v`                       | Keeps MongoDB safe                        |
| **Bind mount option**  | `./mongo-data:/data/db`                                              | Store data directly on host Mac           |
| **Inspect commands**   | `docker volume ls` / `docker volume inspect todo-service_mongo-data` | Check volume existence, path, and details |

---

💡 **Takeaway:**
In your `todo-service` setup, Docker Compose automatically mounts and persists your MongoDB data volume (`todo-service_mongo-data`) on startup.
If you ever want to keep data outside Colima’s internal disk for easier backup, switch to a bind mount like `./mongo-data:/data/db`.
