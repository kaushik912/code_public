Here’s an improved, **ready-reckoner version** of your *OpenRewrite Recipe Development Guide*.
It’s restructured for clarity, adds practical “quick checks,” and highlights what you need for fast Java recipe testing.

---

# 🧩 OpenRewrite Recipe Development Ready-Reckoner

This guide helps you **create, test, and troubleshoot Java recipes quickly** using the OpenRewrite Maven plugin.

---

## ⚙️ Project Setup

### 1. Clone the Starter

```bash
git clone https://github.com/moderneinc/rewrite-recipe-starter
cd rewrite-recipe-starter
```

The starter includes all required dependencies and structure.

### 2. Update Java Version *(Optional)*

In `pom.xml`:

```xml
<maven.compiler.release>21</maven.compiler.release>
```

### 3. Add Test Samples

Create a folder to hold your sample Java files for testing:

```
src/
├── main/java/com/yourorg/
│   └── YourRecipe.java
└── testsamples/
    └── Test.java
```

> 💡 *Some recipes may apply to all files under `src/`, regardless of `<includes>`.*

---

## 🧱 Maven Plugin Configuration

Add to your `pom.xml`:

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>6.22.1</version>
  <configuration>
    <failOnDryRunResults>true</failOnDryRunResults>
    <activeRecipes>
      <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryTrueFalseRecipe</recipe>
      <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryFalseTrueRecipe</recipe>
    </activeRecipes>
  </configuration>

  <dependencies>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-migrate-java</artifactId>
      <version>3.20.0</version>
    </dependency>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-rewrite</artifactId>
      <version>0.14.1</version>
    </dependency>

    <!-- ⚠️ Important: Include the project itself -->
    <dependency>
      <groupId>${project.groupId}</groupId>
      <artifactId>${project.artifactId}</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</plugin>
```

### ✅ Quick Checks

* ✅ Class ends with `Recipe` (e.g., `SimplifyTernaryRecipe`)
* ✅ Nested recipes use `$` (e.g., `OuterRecipe$InnerRecipe`)
* ✅ Project itself is listed as a dependency

---

## 🧪 Testing Recipes

### Run All Active Recipes

```bash
mvn rewrite:run
```

### Preview Without Modifying Code

```bash
mvn rewrite:dryRun
```

### Run a Specific Recipe

```bash
mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.YourRecipeName
```

### Run on a Specific Module

```bash
mvn -pl module-name rewrite:run
```

| Task           | Command                                                          |
| -------------- | ---------------------------------------------------------------- |
| Dry-run all    | `mvn rewrite:dryRun`                                             |
| Run all active | `mvn rewrite:run`                                                |
| Run one recipe | `mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.RecipeName` |
| On module      | `mvn -pl my-module rewrite:run`                                  |

---

## 🧰 Example Recipes

### **Example 1 – SimplifyTernary**

**Source:** [SimplifyTernary.java](https://github.com/moderneinc/rewrite-recipe-starter/blob/main/src/main/java/com/yourorg/SimplifyTernary.java)

**Activate in `pom.xml`:**

```xml
<activeRecipes>
  <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryTrueFalseRecipe</recipe>
  <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryFalseTrueRecipe</recipe>
</activeRecipes>
```

**Run:**

```bash
mvn rewrite:run
```

---

### **Example 2 – EqualsAvoidsNull**

**Source:** [EqualsAvoidsNull.java](https://github.com/moderneinc/rewrite-recipe-starter/blob/main/src/main/java/com/yourorg/EqualsAvoidsNull.java)

**Run directly:**

```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.EqualsAvoidsNullRecipe
```

---

## 🧩 Recipe Authoring Essentials

### Key Annotations

| Annotation          | Purpose                                  |
| ------------------- | ---------------------------------------- |
| `@RecipeDescriptor` | Describes the recipe (name, description) |
| `@BeforeTemplate`   | Defines pattern to match                 |
| `@AfterTemplate`    | Defines replacement code                 |

### Example

```java
@RecipeDescriptor(
    name = "Simplify ternary expressions",
    description = "Replaces redundant ternary operations with simpler expressions."
)
public class SimplifyTernary {

    @BeforeTemplate
    boolean before(boolean expr) {
        return expr ? true : false;
    }

    @AfterTemplate
    boolean after(boolean expr) {
        return expr;
    }
}
```

**Result:**
During build, OpenRewrite generates `SimplifyTernaryRecipe.java` automatically.

---

## 🛠 Auto-Generated Recipe Files

| Stage  | Example File                 | Purpose                          |
| ------ | ---------------------------- | -------------------------------- |
| Source | `SimplifyTernary.java`       | You write annotated recipe       |
| Build  | *Auto-generated*             | Created by annotation processing |
| Output | `SimplifyTernaryRecipe.java` | Used at runtime by OpenRewrite   |

---


