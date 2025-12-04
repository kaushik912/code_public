
# 🐳 **Docker & Docker Compose Cheatsheet (for todo-service)**

## ⚙️ **Setup & Basics**

| Action                           | Command                            | Notes                                      |
| -------------------------------- | ---------------------------------- | ------------------------------------------ |
| Start all services in background | `docker compose up -d`             | Most common way to start your stack        |
| Stop all services                | `docker compose down`              | Stops & removes containers (keeps volumes) |
| Stop + delete volumes            | `docker compose down -v`           | ⚠️ Deletes data volumes                    |
| View status of services          | `docker compose ps`                | Shows which containers are up              |
| View service logs (follow)       | `docker compose logs -f`           | Stream logs for all services               |
| View one service’s logs          | `docker compose logs -f mongo`     | Example: show MongoDB logs only            |
| Stop services without removing   | `docker compose stop`              | Keeps containers around (paused)           |
| Restart services                 | `docker compose start`             | Restarts stopped containers                |
| Rebuild images                   | `docker compose build`             | Rebuild Docker images from Dockerfile      |
| Recreate + restart everything    | `docker compose up -d --build`     | Useful after code or Dockerfile changes    |
| Restart one service              | `docker compose restart app`       | Gracefully restart your app only           |
| List all defined services        | `docker compose config --services` | Handy check                                |
| Check Compose file validity      | `docker compose config`            | Merges and validates compose YAML          |

---

## 🧱 **Volumes & Persistent Data**

| Action                     | Command                                         | Notes                                                   |
| -------------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| List all Docker volumes    | `docker volume ls`                              | Lists all volumes (including `todo-service_mongo-data`) |
| Inspect volume details     | `docker volume inspect todo-service_mongo-data` | Shows mount path & metadata                             |
| Remove unused volumes      | `docker volume prune`                           | Deletes dangling volumes (be cautious)                  |
| Remove one volume manually | `docker volume rm <name>`                       | Example: `docker volume rm todo-service_mongo-data`     |
| Mount custom folder        | `./mongo-data:/data/db`                         | Bind mount for host folder persistence                  |

---

## 📦 **Containers & Images (General Docker)**

| Action                                  | Command                      | Notes                                                                   |
| --------------------------------------- | ---------------------------- | ----------------------------------------------------------------------- |
| List running containers                 | `docker ps`                  | Active ones only                                                        |
| List all containers (including stopped) | `docker ps -a`               | Historical view                                                         |
| Stop one container                      | `docker stop <container_id>` | Graceful stop                                                           |
| Remove one container                    | `docker rm <container_id>`   | Deletes container only                                                  |
| List images                             | `docker images`              | Shows all downloaded/built images                                       |
| Remove image                            | `docker rmi <image_id>`      | Delete unused image                                                     |
| Clean up everything unused              | `docker system prune -a`     | ⚠️ Removes stopped containers, unused networks, images, and build cache |

---

## 🔍 **Debugging & Inspection**

| Action                               | Command                               | Notes                              |
| ------------------------------------ | ------------------------------------- | ---------------------------------- |
| View logs for all containers         | `docker logs <container_name>`        | Works even outside Compose         |
| Shell into running container         | `docker exec -it <container_name> sh` | Or `bash` if available             |
| View environment variables           | `docker exec <container_name> env`    | Useful for debugging configuration |
| Check container’s IP/network info    | `docker inspect <container_name>`     | Shows detailed metadata            |
| Check running processes in container | `docker top <container_name>`         | Shows what’s running inside        |

---

## 💾 **Colima-specific (macOS)**

| Action                                      | Command                                                         | Notes                                      |
| ------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------ |
| SSH into Colima VM                          | `colima ssh`                                                    | Access Linux environment where Docker runs |
| View volumes inside VM                      | `sudo ls /var/lib/docker/volumes`                               | See stored named volumes                   |
| Inspect Mongo data                          | `sudo ls /var/lib/docker/volumes/todo-service_mongo-data/_data` | Real files inside Mongo volume             |
| Restart Colima                              | `colima stop && colima start`                                   | Resets Docker VM                           |
| Delete Colima VM (⚠️ wipes all Docker data) | `colima delete`                                                 | Use only if you want to start fresh        |

---

## 🧰 **Handy Aliases (optional)**

Add these to your `~/.zshrc` or `~/.bashrc` for quicker use:

```bash
alias dcu='docker compose up -d'
alias dcd='docker compose down'
alias dcl='docker compose logs -f'
alias dcs='docker compose stop'
alias dcr='docker compose restart'
alias dcv='docker volume ls'
```

---

## 💡 **Most Common Everyday Commands**

| Use Case                 | Command                                         |
| ------------------------ | ----------------------------------------------- |
| Start everything         | `docker compose up -d`                          |
| Check logs               | `docker compose logs -f`                        |
| Stop cleanly             | `docker compose down`                           |
| Stop temporarily         | `docker compose stop`                           |
| Inspect Mongo volume     | `docker volume inspect todo-service_mongo-data` |
| SSH into Mongo container | `docker exec -it todo-service-mongo sh`         |
| View running services    | `docker compose ps`                             |

---

✅ **Takeaway**

* Use **`up -d` / `down` / `stop` / `start`** to control your stack.
* Use **named volumes** (like `todo-service_mongo-data`) to persist data.
* Use **`docker volume inspect`** to find where that data actually lives.
* Use **bind mounts (`./mongo-data:/data/db`)** only if you want host-level access.
* Regularly clean up with `docker system prune -a` (carefully).


---

### 🧠 mental model

Think of it like this( `docker compose stop` versus `docker compose down`):

> `stop` = press **pause** ⏸️

> `down` = press **eject** ⏏️ (containers gone, volume optional)

---

## 🧩 What “`app`” really refers to

When you run:

```bash
docker compose restart app
```

➡️ The word **`app`** here is **not** related to:

* your container’s **`WORKDIR`** (`/app`),
* or the **filename** of your JAR (`app.jar`).

Instead, it refers to the **service name** defined in your `docker-compose.yml`.

---

## 🧱 Example

Here’s the key part of your Compose file:

```yaml
services:
  mongo:
    image: mongo:7
    ...
  app:
    build: .
    container_name: todo-service
    depends_on:
      - mongo
    ports:
      - "8080:8080"
    environment:
      SPRING_DATA_MONGODB_URI: mongodb://mongo:27017/todos
```

→ The word **`app`** under `services:` is the **service name**.
This is what Compose uses to refer to that container in its internal network and CLI commands.

So:

* `docker compose restart app` = restart the service named **app**
* `docker compose restart mongo` = restart MongoDB service

It has **nothing to do with `/app` or `app.jar`** — those are just conventions you used inside the image.

---

## 🧠 How Compose ties it together

| Term               | Defined in           | Example          | Meaning                                       |
| ------------------ | -------------------- | ---------------- | --------------------------------------------- |
| **Service name**   | `docker-compose.yml` | `app`, `mongo`   | Logical name in the Compose project           |
| **Container name** | `container_name:`    | `todo-service`   | Actual container’s name in Docker             |
| **WORKDIR**        | Dockerfile           | `/app`           | Directory where commands run inside container |
| **Executable JAR** | In Dockerfile        | `app.jar`        | Your compiled Spring Boot app                 |
| **Network alias**  | Automatic            | `app` or `mongo` | How services talk to each other internally    |

So, in your setup:

* **`app`** → Compose service name
* **`todo-service`** → Docker container name
* **`/app`** → working directory inside the container
* **`app.jar`** → Spring Boot JAR file you built and run

---

## ✅ Quick demo

You can confirm the service name list anytime:

```bash
docker compose config --services
```

Example output:

```
app
mongo
```

Now you can restart just your Spring Boot container:

```bash
docker compose restart app
```

Or MongoDB:

```bash
docker compose restart mongo
```

---

### TL;DR

| `app` in this command        | Meaning                                                   |
| ---------------------------- | --------------------------------------------------------- |
| `docker compose restart app` | Restart the service named **app** in `docker-compose.yml` |
| Not related to               | `WORKDIR`, `app.jar`, or image name                       |

---

💡 **Takeaway:**

> The name after `docker compose restart` (or any Compose command like `logs`, `exec`, etc.) always refers to the **service name** from your Compose file — not any file, directory, or container detail.

