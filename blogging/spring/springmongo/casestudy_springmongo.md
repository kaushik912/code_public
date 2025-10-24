Let’s wire up a tiny Spring Boot + MongoDB app and run everything with Docker. you’ll build a basic “todos” API, learn how Spring Initializr fits in, and practice two common Docker flows:

1. run Mongo in a container and your app on your machine
2. run both app + Mongo with docker compose

---

# 0) prerequisites

* Java 21 (or 17+), Maven or Gradle
* Docker Desktop (or Docker Engine + Compose v2)
* cURL or a REST client (HTTPie/Postman etc.)

---

# 1) scaffold the initial project 

curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-mongodb \
  -d type=maven-project \
  -d language=java \
  -d name=todo-service \
  -d packageName=com.example.todo \
  -d javaVersion=17 \
  -o todo-service.zip && unzip todo-service.zip -d todo-service


---

# 2) create a simple domain, repo, and controller

## `src/main/java/com/example/todo/Todo.java`

```java
package com.example.todo;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document("todos")
public class Todo {
  @Id
  private String id;
  private String title;
  private boolean done;

  public Todo() {}
  public Todo(String title, boolean done) { this.title = title; this.done = done; }

  public String getId() { return id; }
  public String getTitle() { return title; }
  public boolean isDone() { return done; }

  public void setId(String id) { this.id = id; }
  public void setTitle(String title) { this.title = title; }
  public void setDone(boolean done) { this.done = done; }
}
```

## `src/main/java/com/example/todo/TodoRepository.java`

```java
package com.example.todo;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface TodoRepository extends MongoRepository<Todo, String> {}
```

## `src/main/java/com/example/todo/TodoController.java`

```java
package com.example.todo;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/todos")
public class TodoController {
  private final TodoRepository repo;
  public TodoController(TodoRepository repo) { this.repo = repo; }

  @GetMapping
  public List<Todo> all() { return repo.findAll(); }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public Todo create(@RequestBody Todo body) { return repo.save(body); }

  @GetMapping("/{id}")
  public Todo one(@PathVariable String id) { return repo.findById(id).orElseThrow(); }

  @PutMapping("/{id}")
  public Todo update(@PathVariable String id, @RequestBody Todo body) {
    body.setId(id);
    return repo.save(body);
  }

  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void delete(@PathVariable String id) { repo.deleteById(id); }
}
```

## optional: seed a couple docs on startup

`src/main/java/com/example/todo/SeedData.java`

```java
package com.example.todo;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SeedData {
  @Bean
  CommandLineRunner init(TodoRepository repo) {
    return args -> {
      if (repo.count() == 0) {
        repo.save(new Todo("learn docker", false));
        repo.save(new Todo("wire spring + mongo", false));
      }
    };
  }
}
```

---

# 3) config: local vs container

We’ll make the MongoDB URI configurable via env var with a fallback for local dev.

`src/main/resources/application.properties`

```properties
# Default for local dev (Mongo on localhost:27017)
spring.data.mongodb.uri=${SPRING_DATA_MONGODB_URI:mongodb://localhost:27017/todos}

# server port (we’ll keep 8080)
server.port=8080
```

---

# 4) path A — run Mongo in Docker, app locally

### 4.1 start Mongo container

```bash
docker run -d --name mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_DATABASE=todos \
  mongo:7
```

### 4.2 run the app (from project root)

```bash
./mvnw spring-boot:run
# or ./gradlew bootRun
```

### 4.3 try the API

```bash
# list (seeded docs appear after first run if you added SeedData)
curl http://localhost:8080/api/todos

# create
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"try docker compose","done":false}'

# update
curl -X PUT http://localhost:8080/api/todos/{id} \
  -H "Content-Type: application/json" \
  -d '{"title":"try docker compose","done":true}'

# delete
curl -X DELETE http://localhost:8080/api/todos/{id}
```

This flow is great during development: you get a real Mongo without installing it locally, while keeping fast Spring dev loops.

---

# 5) path B — Dockerize the app + use docker compose

## 5.1 create a production-ready Dockerfile (Maven, multi-stage)

`Dockerfile`

```dockerfile
# 1) build stage
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

# 2) runtime stage (small JRE)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
# optional: add non-root user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
# SPRING_DATA_MONGODB_URI will be injected by compose
ENTRYPOINT ["java","-jar","/app/app.jar"]
```

*(If you use Gradle, swap the builder base image and build command accordingly.)*

## 5.2 compose both services

`docker-compose.yml`

```yaml
services:
  mongo:
    image: mongo:7
    container_name: mongo
    ports:
      - "27017:27017"   # optional expose (handy for debugging)
    environment:
      MONGO_INITDB_DATABASE: todos
    volumes:
      - mongo-data:/data/db

  app:
    build: .
    container_name: todo-service
    depends_on:
      - mongo
    ports:
      - "8080:8080"
    environment:
      # Notice the hostname is the *service name* "mongo" inside the compose network
      SPRING_DATA_MONGODB_URI: mongodb://mongo:27017/todos

volumes:
  mongo-data:
```

## 5.3 build & run

```bash
docker compose build
docker compose up
# (add -d to run detached)
```

## 5.4 try the API (containers)

```bash
curl http://localhost:8080/api/todos
```

---

# 6) common Docker commands you’ll use

* **see containers**: `docker ps -a`
* **logs**:

  * single: `docker logs -f mongo`
  * compose stack: `docker compose logs -f app`
* **exec into a container** (Mongo shell via mongosh image is easiest, else bash):

  ```bash
  docker exec -it mongo sh
  ```
* **stop / remove**:

  * compose: `docker compose down` (add `-v` to remove volumes)
  * single: `docker stop mongo && docker rm mongo`
* **rebuild app image after code changes**:

  * `docker compose build app && docker compose up -d app`

---

# 7) quick variations to learn the pieces

1. **Change DB name**

   * Set `SPRING_DATA_MONGODB_URI=mongodb://mongo:27017/mydb` in compose and watch Spring connect to a new database.

2. **Use profiles**

   * Add `application-docker.properties` with `spring.data.mongodb.uri=mongodb://mongo:27017/todos`.
   * Start app container with `SPRING_PROFILES_ACTIVE=docker` to see how Spring profiles swap configs.

3. **Healthcheck** (compose)

```yaml
  app:
    # ...
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/actuator/health"]
      interval: 10s
      timeout: 3s
      retries: 3
```

*(Add `spring-boot-starter-actuator` to dependencies and `management.endpoints.web.exposure.include=health` to properties.)*

4. **Persist data**

   * You already used a named volume `mongo-data`. Delete and recreate containers; your todos stick because the volume remains.

5. **Run tests in CI-like Docker build**

   * Remove `-DskipTests` in the Dockerfile build stage to enforce tests.

---

# 8) troubleshooting tips

* **“Connection refused” to Mongo**

  * When using compose, the hostname inside the app container must be `mongo` (the service name), not `localhost`.
* **Port conflicts**

  * Change the left side of `ports`: e.g., `"28017:27017"` if 27017 is busy.
* **Rebuilding but seeing old code**

  * Use `docker compose build --no-cache app`.

---

# 9) what you just learned (mental model)

* Spring Initializr gives you a clean Boot starter with Mongo support.
* For **dev**, it’s common to run Mongo in Docker and your app locally.
* For **prod-like**, package the app into a Docker image and orchestrate the app + database with **docker compose**.
* Environment variables (like `SPRING_DATA_MONGODB_URI`) keep your image generic and twelve-factor friendly.

---

# Mongo Debugging
## 🧩 if MongoDB is running in Docker (like `docker run -d --name mongo …`)

### 1️⃣ open a shell inside the container

```bash
docker exec -it mongo bash
```

if the container image doesn’t have `mongosh` built in (most `mongo:7` images do), then:

```bash
mongosh
```

or, if you’re on an older `mongo` image that still uses `mongo` CLI:

```bash
mongo
```

---

### 2️⃣ connect from **outside** the container using your host’s mongo shell

if you have `mongosh` installed locally:

```bash
mongosh "mongodb://localhost:27017/todos"
```

---

### 3️⃣ check what’s in the DB

once inside `mongosh`:

```javascript
show dbs             // lists databases; you should see 'todos'
use todos            // switch to your DB
show collections     // should show 'todos'
db.todos.find().pretty()  // view documents
```

you should see something like:

```json
[
  { "_id": "665...", "title": "learn docker", "done": false },
  { "_id": "666...", "title": "wire spring + mongo", "done": false }
]
```

---

## 🧩 if you’re using docker-compose

you can jump into the mongo service directly:

```bash
docker compose exec mongo mongosh
```

then same commands inside:

```javascript
use todos
show collections
db.todos.find().pretty()
```

---

## 🧩 if you didn’t specify an auth user

the commands above work as-is.
if you set environment variables like `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`, you’d log in as:

```bash
mongosh "mongodb://<user>:<pass>@localhost:27017/todos"
```

---

## ✅ verify seed executed

if you see the docs, your `CommandLineRunner` ran fine.

if the `todos` collection is missing or empty:

* make sure your repo was actually detected (fix “0 MongoDB repository interfaces” first)
* restart the app after fixing; the `SeedData` runs at startup when the context loads successfully.

---
