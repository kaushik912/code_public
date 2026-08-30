# 🧩 POM Version Upgrade with OpenRewrite

This example demonstrates how to use **OpenRewrite** to automatically upgrade the **Spring Boot parent version** in your project’s `pom.xml`.

---

## 1️⃣ Set up your starting version

In your `pom.xml`, bring down the Spring Boot parent version to an older release — for example **3.5.3** — so that we have a change to apply.

```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>3.5.3</version>
  <relativePath/> <!-- lookup parent from repository -->
</parent>
```

This will serve as the “before” state that we’ll upgrade automatically.

---

## 2️⃣ Define the OpenRewrite recipe

Next, modify your `rewrite.yml` file to include a recipe that upgrades the parent version to **3.5.7**.

```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.acme.BumpBootParent
displayName: "Upgrade Spring Boot parent to 3.5.7"
recipeList:
  - org.openrewrite.maven.UpgradeParentVersion:
      groupId: "org.springframework.boot"
      artifactId: "spring-boot-starter-parent"
      newVersion: "3.5.7"
```

Here:

* `groupId` and `artifactId` **must match exactly** with those in your `pom.xml` parent section.
* `newVersion` specifies the target version you want to upgrade to.

---

## 3️⃣ Run the dry run

From the project root, execute:

```bash
mvn clean rewrite:dryRun
```

OpenRewrite will:

1. Analyze your `pom.xml`
2. Detect that the parent version `3.5.3` can be upgraded to `3.5.7`
3. Generate a patch showing the proposed change

---

## 4️⃣ Review the generated patch

Check the patch file (usually located at `target/rewrite/rewrite.patch`):

```diff
--- a/pom.xml
+++ b/pom.xml
@@ -3,7 +3,7 @@
   <parent>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-starter-parent</artifactId>
-    <version>3.5.3</version>
+    <version>3.5.7</version>
     <relativePath/> <!-- lookup parent from repository -->
   </parent>
```

✅ This confirms the recipe successfully identified and prepared the version bump.

---

## 5️⃣ Apply the change

When satisfied with the patch, apply the recipe to update the file directly:

```bash
mvn rewrite:run
```

or, if you prefer using Git:

```bash
git apply target/rewrite/rewrite.patch
```

After applying, your `pom.xml` should now list the new Spring Boot version:

```xml
<version>3.5.7</version>
```

---

### 🧠 Key Takeaways

* The `org.openrewrite.maven.UpgradeParentVersion` recipe is purpose-built for **upgrading parent POM versions**.
* Ensure that the **groupId** and **artifactId** in your recipe match your actual parent declaration exactly.
* Always start with a **dry run** to preview and verify the patch before applying.
* You can chain multiple recipes in one `rewrite.yml` to handle other dependency or configuration upgrades together.

