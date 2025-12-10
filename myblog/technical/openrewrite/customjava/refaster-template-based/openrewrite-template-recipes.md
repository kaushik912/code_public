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

Add the following recipes to your `pom.xml`:

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

    <!-- ⚠️ Important: Include the project itself as generated recipes are present in project itself in this case-->
    <dependency>
      <groupId>${project.groupId}</groupId>
      <artifactId>${project.artifactId}</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</plugin>
```

---

## 🚀 Running Recipes

Once you've configured the plugin, execute your recipes:

```bash
mvn rewrite:run
```

This command will:
- Apply all recipes listed in `<activeRecipes>`
- Modify files in place based on the transformations
- Fail the build if `<failOnDryRunResults>true` and changes are detected

**Dry-run mode** (preview changes without applying):
```bash
mvn rewrite:dryRun
```

---

## 📚 Recipe Examples Explained

The following sections explain the recipes referenced in the Maven configuration above.

### **Example 1: SimplifyTernary (Multi-Recipe Pattern)**

**File:** [SimplifyTernary.java](../src/main/java/com/yourorg/SimplifyTernary.java)

**Understanding the SimplifyTernary Recipe Structure:**

The `SimplifyTernary.java` file demonstrates a **multi-recipe pattern** using Refaster templates. Here's how it works:

#### 1. **Class-Level `@RecipeDescriptor`**
```java
@RecipeDescriptor(
    name = "Simplify ternary expressions",
    description = "Simplifies various types of ternary expressions to improve code readability."
)
public class SimplifyTernary {
```
- This annotation defines metadata for the **parent recipe**
- The class itself does **not** extend `Recipe` — OpenRewrite generates a `SimplifyTernaryRecipes` class for you
- This becomes the umbrella recipe that groups related transformations

#### 2. **Nested Static Classes for Individual Recipes**
```java
@RecipeDescriptor(
    name = "Replace `booleanExpression ? true : false` with `booleanExpression`",
    description = "Replace ternary expressions like `booleanExpression ? true : false` with `booleanExpression`."
)
public static class SimplifyTernaryTrueFalse {
```
- Each nested class represents a **separate recipe**
- Each has its own `@RecipeDescriptor` with specific name and description
- These become individual recipes you can reference independently

#### 3. **Template Methods: `@BeforeTemplate` and `@AfterTemplate`**
```java
@BeforeTemplate
boolean before(boolean expr) {
    return expr ? true : false;
}

@AfterTemplate
boolean after(boolean expr) {
    return expr;
}
```
- `@BeforeTemplate`: Defines the **pattern to match** in existing code
- `@AfterTemplate`: Defines what the code **should look like** after transformation
- OpenRewrite uses pattern matching to find code matching the `before` template and replaces it with the `after` template
- Parameters (like `expr`) are bound during matching and substituted in the replacement

#### 4. **Generated Recipe Naming Convention**
When you have nested recipes, OpenRewrite generates:
- `SimplifyTernaryRecipes` (note the plural "Recipes")
  - `SimplifyTernaryRecipes$SimplifyTernaryTrueFalseRecipe`
  - `SimplifyTernaryRecipes$SimplifyTernaryFalseTrueRecipe`

Each nested class gets `Recipe` appended to its name in the generated code.

#### 5. **How It Transforms Code**
Example transformation by `SimplifyTernaryTrueFalse`:
```java
// Before
boolean result = isValid() ? true : false;

// After
boolean result = isValid();
```

Example transformation by `SimplifyTernaryFalseTrue`:
```java
// Before
boolean result = isValid() ? false : true;

// After
boolean result = !isValid();
```


---

### **Example 2: EqualsAvoidsNull**

**File:** [EqualsAvoidsNull.java](../src/main/java/com/yourorg/EqualsAvoidsNull.java)

This recipe demonstrates another common pattern for improving code safety.

**Run this recipe directly from command line:**

```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.EqualsAvoidsNullRecipe
```

> 💡 **Tip:** Use `-Drewrite.activeRecipes` to run a specific recipe without modifying `pom.xml`

---

### **Example 3: PrintHello (Simple Single-Recipe Pattern)**

**File:** [PrintHello.java]

The `PrintHello` recipe demonstrates the **simplest form** of a Refaster template recipe — a single transformation without nested classes.

### **Recipe Structure**

```java
@RecipeDescriptor(
    name = "Say Hello Recipe",
    description = "Replaces a simple print statement with a configurable greeting message."
)
@SuppressWarnings("unused")
public class PrintHello {

    @BeforeTemplate
    void before() {
        System.out.println("Hello!");
    }

    @AfterTemplate
    void after() {
        System.out.println("Hello from " + "Kaushik !");
    }
}
```

### **Key Differences from SimplifyTernary**

| Aspect | SimplifyTernary | PrintHello |
|--------|----------------|------------|
| **Structure** | Multiple nested static classes | Single flat class |
| **Recipes Generated** | Multiple (`SimplifyTernaryRecipes$*`) | One (`PrintHelloRecipe`) |
| **Use Case** | Grouping related transformations | Single, specific transformation |
| **Reference Name** | `com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryTrueFalseRecipe` | `com.yourorg.PrintHelloRecipe` |

### **How It Works**

1. **Pattern Matching**: OpenRewrite scans your code for exact matches of:
   ```java
   System.out.println("Hello!");
   ```

2. **Replacement**: When found, it replaces with:
   ```java
   System.out.println("Hello from " + "Kaushik !");
   ```

3. **Generated Recipe**: OpenRewrite generates `PrintHelloRecipe` (note: singular "Recipe", not "Recipes")

### **Running PrintHello**

Add to your `pom.xml` activeRecipes:
```xml
<activeRecipes>
  <recipe>com.yourorg.PrintHelloRecipe</recipe>
</activeRecipes>
```

Or run directly:
```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.PrintHelloRecipe
```

### **When to Use Each Pattern**

- **Use Nested Classes (like SimplifyTernary)** when:
  - You have multiple related transformations
  - You want to group recipes logically
  - Users might want to apply recipes individually or as a group

- **Use Single Class (like PrintHello)** when:
  - You have one specific transformation
  - The recipe is standalone and self-contained
  - Simplicity is preferred

---
