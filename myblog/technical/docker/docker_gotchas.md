# Docker Commands Cheat Sheet

## 🧹 Cleanup Commands

### Remove a Single Image
```bash
docker image rm 6d07f9671c19
````

### Remove a Single Container

```bash
docker container rm f117fbbc2d4f
```

### Get IDs of All Containers

```bash
docker ps -aq
```

### Remove All Containers

```bash
docker rm $(docker ps -aq)
```

### Remove All Images

```bash
docker rmi $(docker images -a -q)
```

> **Note:** Use `--force` to forcibly delete an image, especially when it's used by a stopped container:

```bash
docker rmi <image_ID> --force
```

### Run and Remove a Container Immediately After Exit

```bash
docker run --rm image_name
```

---

## 📦 Docker Usage & Image Management

### Check Docker Disk Usage

```bash
docker system df
```

### Commit an Existing Container to an Image

```bash
docker container commit 1f26240ecaff dockerhub.orgcorp.com/nodemaven:v0.2
```

### Build an Image from a Dockerfile

```bash
docker image build -t dockerhub.orgcorp.com/nodemvn:v0.1 .
```

### Tag an Existing Image with a New Name

First, get the image ID, then:

```bash
docker image tag d583c3ac45fd myname/server:latest
```

### Run an Image Interactively

```bash
docker run -it dockerhub.orgcorp.com/alpine:latest /bin/ash
docker container run -it dockerhub.orgcorp.com/ubuntu:16.04 /bin/bash
```

### Pull an Image from a Registry

```bash
docker image pull dockerhub.orgcorp.com/ubuntu:16.04
```

### Push an Image to a Registry

```bash
docker push dockerhub.orgcorp.com/nodemaven:v0.2
```

### List All Images

```bash
docker image ls
```

### List All Containers (Running and Stopped)

```bash
docker container ls -a
```

### Run a Container in Detached Mode (Daemon)

```bash
docker container run --detach --publish 8080:8080 dockerhub.orgcorp.com/tomcat:8.0-jre8
```

> This will run Tomcat and expose it on port `8080`.

---

## 🔁 Container Lifecycle Management

### Restart the Last Exited Container

#### Step-by-Step:

Start the last container in the background:

```bash
docker start $(docker ps -q -l)
```

Reattach the terminal and stdin:

```bash
docker attach $(docker ps -q -l)
```

#### One-Liner to Start and Attach:

```bash
docker start -a -i $(docker ps -q -l)
```

#### Explanation of Options:

* `docker start`: Start a stopped container

  * `-a`: Attach to the container
  * `-i`: Interactive mode
* `docker ps`: List containers

  * `-q`: Show only container IDs
  * `-l`: Show only the last created container

### Check the Running Size of Containers

```bash
docker container ls -s
```


