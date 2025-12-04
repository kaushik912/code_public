# 🚀 OpenRewrite Quickstart — Rename Property in Spring Boot Project

This guide walks through using **OpenRewrite** to automatically rename a property key inside a **Spring Boot “hello-world”** project.

---

## 1️⃣ Create a sample Spring Boot web project

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web \
  -d type=maven-project \
  -d language=java \
  -d name=hello-world \
  -d packageName=com.example.helloworld \
  -d javaVersion=17 \
  -o hello-world.zip && unzip hello-world.zip -d hello-world
```

This downloads and unpacks a minimal Spring Boot project using **Java 17** and the **Spring Web** starter.

---

## 2️⃣ Add the OpenRewrite plugin to your POM

Edit `hello-world/pom.xml` and add this plugin inside `<build><plugins>`:

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>5.2.6</version>
</plugin>
```

This adds OpenRewrite’s Maven plugin to your project. You’ll use it to run and test your recipes.

---

## 3️⃣ Add a custom property to `application.properties`

Open `src/main/resources/application.properties` and add:

```properties
server.timeout=5000
```

This is the property we’ll migrate to a new key.

---

## 4️⃣ Create a recipe to rename the property key

Create a new file in the project root called `rewrite.yml`:

```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.acme.RenameServerTimeout
displayName: "Rename server.timeout → server.request-timeout (properties)"
recipeList:
  - org.openrewrite.properties.ChangePropertyKey:
      oldPropertyKey: "server.timeout"
      newPropertyKey: "server.request-timeout"
```

This recipe uses OpenRewrite’s built-in `ChangePropertyKey` to safely rename the key across all `.properties` files.

---

## 5️⃣ Configure the plugin to activate the recipe

Update your plugin section in `pom.xml` as follows:

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>5.2.6</version>
  <configuration>
    <activeRecipes>
      <recipe>com.acme.RenameServerTimeout</recipe>
    </activeRecipes>
    <configLocation>rewrite.yml</configLocation>
  </configuration>
</plugin>
```

📌 **Notes:**

* Place this plugin **above** the `spring-boot-maven-plugin` (ordering rarely matters but helps readability).
* Version **5.2.6** avoids duplicate executions observed with newer plugin versions.

---

## 6️⃣ Build once before running Rewrite

```bash
mvn clean install -DskipTests
```

Building first ensures all dependencies and classpaths are resolved, speeding up Rewrite’s later steps.

---

## 7️⃣ Preview changes (dry run)

Run a dry run to see what changes the recipe would make:

```bash
mvn clean rewrite:dryRun
```

> Add `-q` for quieter output:
> `mvn -q clean rewrite:dryRun`

---

## 8️⃣ Review the generated patch file

Open:

```
target/rewrite/rewrite.patch
```

You’ll see a Git-style diff showing the old and new property key.

---

## 9️⃣ Apply the recipe

You can apply changes either via OpenRewrite or Git:

**Option A — Let Rewrite apply automatically**

```bash
mvn rewrite:run
```

**Option B — Apply manually using Git**

```bash
git apply --check target/rewrite/rewrite.patch   # validate
git apply target/rewrite/rewrite.patch           # apply instantly
```

Using `git apply` is very fast and produces the same result.

---

## ⚡ Typical performance

* First run (`rewrite:dryRun` or `rewrite:run`) takes ~**1 minute**
  (mostly during *“Resolving POMs”*).
* Add memory tuning to improve it.

```bash
export MAVEN_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=100"
```

⏱️ After tuning: ~50 s

---

## ⚙️ Run a single recipe directly

```bash
mvn rewrite:dryRun -Drewrite.activeRecipes=com.acme.RenameServerTimeout
```

This overrides the configuration in `pom.xml` for quick testing.

---

## 🚀 Boost performance with parallel + offline mode

* `-T 1C` → one thread per CPU core
* `-o` → offline mode (skip dependency resolution)

Example:

```bash
mvn -o -T 1C rewrite:dryRun
```

⏱️ On a 10-core Mac, this reduced runtime to ~**19 seconds**!

---

## ✅ Summary

| Step | Command / File                   | Purpose                              |
| ---- | -------------------------------- | ------------------------------------ |
| 1    | `curl …`                         | Create Spring Boot “hello-world” app |
| 2    | Add `rewrite-maven-plugin`       | Enable OpenRewrite                   |
| 3    | Add property                     | Something to migrate                 |
| 4    | `rewrite.yml`                    | Define rename recipe                 |
| 5    | Configure plugin                 | Activate recipe                      |
| 6    | `mvn clean install -DskipTests`  | Prebuild project                     |
| 7    | `mvn rewrite:dryRun`             | Preview changes                      |
| 8    | `target/rewrite/rewrite.patch`   | Review diff                          |
| 9    | `mvn rewrite:run` or `git apply` | Apply transformation                 |

---

✅ **Result:**
Your `application.properties` now contains:

```properties
server.request-timeout=5000
```

with all formatting preserved — fully automated by OpenRewrite.
