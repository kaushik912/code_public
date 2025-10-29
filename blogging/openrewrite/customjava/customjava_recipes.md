# OpenRewrite Recipe Development Guide

## Setup

### 1. Clone Starter Project
```bash
git clone https://github.com/moderneinc/rewrite-recipe-starter
```
The starter comes pre-configured with all necessary dependencies.

### 2. Update Java Version (Optional)
```xml
<maven.compiler.release>21</maven.compiler.release>
```

### 3. Create Test Folder
Create `src/testsamples/` for viewing recipe outputs for specific files:
```
src/
├── main/java/
│   └── com/yourorg/
│       └── YourRecipe.java
└── testsamples/
    └── Test.java
```

**Note:** Recipes run on all files in `src/`, regardless of `<includes>` configuration. 
- This step is to optionally see your expected results.
- Refer to `samplefiles` folder for sample files to test.

## Maven Plugin Configuration

### Basic Setup
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
        <!-- ⚠️ IMPORTANT: Include the project itself as a dependency -->
        <!-- This makes your recipes available to the plugin -->
        <dependency>
            <groupId>${project.groupId}</groupId>
            <artifactId>${project.artifactId}</artifactId>
            <version>${project.version}</version>
        </dependency>
    </dependencies>
</plugin>
```

### Key Points
- Recipe class names must have the `Recipe` suffix (e.g., `SimplifyTernaryRecipe`)
- Nested recipes use `$` notation: `SimplifyTernary$SimplifyTernaryTrueFalseRecipe`
- Must include project dependency in plugin dependencies

---

## Example 1: SimplifyTernary Recipe

### Step 1: Get Recipe File

Reference the recipe implementation:
https://github.com/moderneinc/rewrite-recipe-starter/blob/main/src/main/java/com/yourorg/SimplifyTernary.java

### Step 2: Update pom.xml

Configure the recipes in `<configuration>`:

```xml
<activeRecipes>
    <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryTrueFalseRecipe</recipe>
    <recipe>com.yourorg.SimplifyTernaryRecipes$SimplifyTernaryFalseTrueRecipe</recipe>
</activeRecipes>
```

### Step 3: Run the Recipe

```bash
mvn rewrite:run
```

---

## Example 2: EqualsAvoidsNull Recipe

### Step 1: Get Recipe File

Reference the recipe implementation:
https://github.com/moderneinc/rewrite-recipe-starter/blob/main/src/main/java/com/yourorg/EqualsAvoidsNull.java

### Step 2: Run Specific Recipe via Command Line

```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.EqualsAvoidsNullRecipe
```

---

## Running Recipes - Quick Commands

| Task | Command |
|---|---|
| Run all active recipes | `mvn rewrite:run` |
| Preview changes (dry run) | `mvn rewrite:dryRun` |
| Run specific recipe | `mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.RecipeName` |
| Run on module | `mvn -pl module-name rewrite:run` |

## Recipe Naming Convention

| Source File | Recipe Class Name |
|---|---|
| `SimplifyTernary.java` | `SimplifyTernaryRecipes` |
| `EqualsAvoidsNull.java` | `EqualsAvoidsNullRecipe` |
| Nested recipes | `OuterRecipe$InnerRecipe` |

## Common Issues

### Recipe Not Found
- Add `Recipe` suffix to class name
- Add project dependency to plugin dependencies
- Use `$` notation for nested classes: `OuterRecipe$InnerRecipe`
