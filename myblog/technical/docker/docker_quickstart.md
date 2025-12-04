# 🚀 Docker Quickstart Guide

Welcome to this quick reference for working with Docker locally.
This page covers setup, cleanup, working with common public images, and using Make to simplify workflows.

---

## 🧪 Getting Started: Hello World

To verify your Docker installation:

```bash
colima start
docker run hello-world
```

---

## 🧹 Docker Cleanup Commands

### 🧨 Remove All Containers

```bash
docker rm -f $(docker ps -a -q)
```

> ⚠️ **Warning:** This will delete *all* containers on your system.

---

### 🗑️ Remove All Images

```bash
docker rmi -f $(docker images -q)
```

> Use with caution—this removes **all** image layers from local storage.

---

# 🐳 Commonly Used Public Base Images

Below are some widely-used images you can pull from Docker Hub.

### ✔️ JDK + Maven (OpenJDK-based)

```
docker run -it maven:3.9.6-eclipse-temurin-17 /bin/bash
```

### ✔️ Node.js (Build Tools Included)

```
docker run -it node:20 /bin/bash
```

### ✔️ General Purpose Alpine Linux

```
docker run -it alpine:latest /bin/sh
```

---

## 📤 Pushing Modified Images

If you’ve modified a running container and want to tag and push it:

### 1️⃣ Commit Container Changes to a New Image

```bash
docker container commit <container_id> myrepo/nodemaven:v0.2
```

### 2️⃣ Push the New Tag to Docker Hub (or any registry)

```bash
docker push myrepo/nodemaven:v0.2
```

> Replace `myrepo` with your Docker Hub username or registry URL.

---

### 📦 Building from a Dockerfile

If you have a Dockerfile in your directory:

```bash
docker image build -t myrepo/nodemaven:v0.1 .
```

---

# 🛠️ Using `make` for a Streamlined Workflow

Rather than typing Docker commands manually, you can create a Makefile to simplify repeat tasks.

## 📄 Example Makefile

```makefile
build:
	docker build -t dev_container .

run:
	docker run -it --rm dev_container

shell:
	docker run -it --rm dev_container /bin/bash
```

---

## ▶️ Running Make Targets

```bash
make run
make shell
```

