# 🧭 OpenRewrite Setup & Usage Guide

This guide explains how to set up and use **OpenRewrite** with Maven for code cleanup, modernization, and static analysis.
The examples below use **Java 21** and the **Spring Initializr** to generate a demo project.

---

## 🚀 Project Creation

Start by generating a sample Spring Boot project targeting Java 21:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web \
  -d type=maven-project \
  -d language=java \
  -d name=hello-world \
  -d packageName=com.example.helloworld \
  -d javaVersion=21 \
  -o hello-world.zip && unzip hello-world.zip -d hello-world
```

Then open the project folder:

```bash
cd hello-world
```

---

## ⚙️ Add OpenRewrite Plugin

Add the following plugin configuration to your `pom.xml` under `<build><plugins>`.

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>6.22.1</version>
  <configuration>
    <exportDatatables>true</exportDatatables>
    <activeRecipes>
      <recipe>org.openrewrite.staticanalysis.CodeCleanup</recipe>
    </activeRecipes>
  </configuration>
  <dependencies>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-static-analysis</artifactId>
      <version>2.20.0</version>
    </dependency>
  </dependencies>
</plugin>
```

This setup:

* Enables **static-analysis recipes**.
* Exports datatables (rewrite metrics/reports).
* Activates `CodeCleanup` by default.

---

## 🔍 Discover Available Recipes

List all recipes available from your configured dependencies:

```bash
mvn rewrite:discover
```

This prints out a tree of available recipes (both built-in and from your recipe JARs).

---

## 🧹 Run Static-Analysis and Cleanup Recipes

Run multiple static-analysis recipes in a single command:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.activeRecipes=\
org.openrewrite.staticanalysis.MissingOverrideAnnotation,\
org.openrewrite.staticanalysis.SimplifyBooleanExpression,\
org.openrewrite.staticanalysis.SimplifyBooleanReturn,\
org.openrewrite.staticanalysis.UseDiamondOperator,\
org.openrewrite.staticanalysis.CodeCleanup,\
org.openrewrite.staticanalysis.CommonStaticAnalysis,\
org.openrewrite.java.RemoveUnusedImports,\
org.openrewrite.java.OrderImports
```

Run a single recipe, for example, removing unused local variables:

```bash
mvn rewrite:run -Drewrite.activeRecipes=org.openrewrite.staticanalysis.RemoveUnusedLocalVariables
```

---

## ✨ Formatting and Auto-Fix Examples

Auto-format the code:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.activeRecipes=org.openrewrite.java.format.AutoFormat \
  -Drewrite.exportDatatables=true
```

Apply Java best-practice recipes:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-rewrite:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.recipes.JavaRecipeBestPractices \
  -Drewrite.exportDatatables=true
```

Migrate Java utility APIs to modern equivalents:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-migrate-java:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.migrate.util.JavaUtilAPIs \
  -Drewrite.exportDatatables=true
```

---

## 🧩 Plugin Command Reference

### 1. Standard shorthand

```bash
mvn rewrite:run -Drewrite.activeRecipes=<recipe>
```

**Behavior:**

* Uses the plugin declared in your `pom.xml`.
* Relies on locally cached plugin and recipe versions.
* Fast, stable, ideal for routine runs.

### 2. Fully qualified with `-U`

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run -Drewrite.activeRecipes=<recipe>
```

**Behavior:**

* Explicitly declares the plugin coordinates.
* The `-U` flag forces Maven to update plugin snapshots and dependencies.
* Useful when testing newer plugin or recipe versions.

| Command                                                 | Uses Plugin from POM? | Forces Update? | When to Use                   |
| ------------------------------------------------------- | --------------------- | -------------- | ----------------------------- |
| `mvn rewrite:run`                                       | ✅ Yes                 | ❌ No           | Routine use                   |
| `mvn -U org.openrewrite.maven:rewrite-maven-plugin:run` | ❌ Not required        | ✅ Yes          | Testing latest plugin/recipes |

---

Here’s a single “all-in-one” Maven command that pulls recipes from **static-analysis**, **migrate-java**, and **best-practices**, then runs a useful bundle (cleanup, formatting, imports, Java util API modernizations), and exports datatables:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.exportDatatables=true \
  -Drewrite.recipeArtifactCoordinates=\
org.openrewrite.recipe:rewrite-static-analysis:RELEASE,\
org.openrewrite.recipe:rewrite-migrate-java:RELEASE,\
org.openrewrite.recipe:rewrite-rewrite:RELEASE \
  -Drewrite.activeRecipes=\
org.openrewrite.staticanalysis.CommonStaticAnalysis,\
org.openrewrite.staticanalysis.CodeCleanup,\
org.openrewrite.java.format.AutoFormat,\
org.openrewrite.java.RemoveUnusedImports,\
org.openrewrite.java.OrderImports,\
org.openrewrite.recipes.rewrite.OpenRewriteRecipeBestPractices,\
org.openrewrite.java.recipes.JavaRecipeBestPractices,\
org.openrewrite.java.migrate.util.JavaUtilAPIs
```

* `-Drewrite.recipeArtifactCoordinates` can reference multiple recipe artifacts (comma-separated). ([docs.openrewrite.org][1])
* `-Drewrite.exportDatatables=true` enables report tables for this run. ([docs.openrewrite.org][2])



