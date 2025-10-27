# 🧪 Exercise: “Everyday hygiene + lib upgrade” (Commons Lang + code cleanups)

## 0) Prep the project

Make sure you have the Spring Boot project (your curl command).

## 1) Intentionally add an old dependency + redundant version

Edit `pom.xml` and add:

```xml
<dependencies>
  <!-- Old version on purpose (we'll upgrade it) -->
  <dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-lang3</artifactId>
    <version>3.9</version>
  </dependency>

  <!-- Redundant version; Boot parent already manages this -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.5.7</version>
  </dependency>
</dependencies>
```

> The second one is there **just to be cleaned up** by OpenRewrite.

## 2) Add a tiny controller that uses patterns we’ll fix

Create `src/main/java/com/example/helloworld/HelloController.java`:

```java
package com.example.helloworld;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Objects; // we'll clean Objects.isNull()
import org.apache.commons.lang3.StringUtils; // we'll upgrade this lib

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello(String name) {
        // anti-patterns we’ll auto-fix:
        if (Objects.isNull(name) || StringUtils.isBlank(name)) {
            name = "world";
        }
        return "Hello, " + name + "!";
    }
}
```

## 3) Create a **composite recipe** (`rewrite.yml`)

Put this at the project root:

```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.acme.EverydayHygieneAndCommonsUpgrade
displayName: "Everyday hygiene + commons-lang3 upgrade"
description: >
  Upgrades commons-lang3, removes redundant versions managed by the parent,
  replaces Objects.isNull(...) with x == null, orders/removes imports,
  auto-formats code, and adds a license header.

recipeList:
  # --- POM changes ---
  - org.openrewrite.maven.UpgradeDependencyVersion:
      groupId: "org.apache.commons"
      artifactId: "commons-lang3"
      newVersion: "3.13.0"         # pick a stable target available to you
      allowMajorUpdates: false      # keep it safe: major bumps off
      allowMinorUpdates: true
      allowPatchUpdates: true

  - org.openrewrite.maven.RemoveRedundantDependencyVersions: {}

  # --- Java code cleanups ---
  - org.openrewrite.java.RemoveObjectsIsNull: {}
  - org.openrewrite.java.OrderImports: {}
  - org.openrewrite.java.RemoveUnusedImports: {}
  - org.openrewrite.java.format.AutoFormat: {}

  # --- (Optional) License header; customize owner/year as you like ---
  - org.openrewrite.java.AddLicenseHeader:
      licenseText: |
        /*
         * Copyright (c) 2025, Your Company
         * All rights reserved.
         */
      fileMatcher: "**/*.java"
```

> Notes
> • `RemoveRedundantDependencyVersions` drops `<version>` tags that are already managed by the parent/BOM.
> • `RemoveObjectsIsNull` rewrites `Objects.isNull(x)` → `x == null` (and the negation to `!= null`).
> • The formatting recipes leave your code tidy and consistent.

## 4) Wire the plugin

In `pom.xml` (keep the plugin version you’ve already validated):

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.openrewrite.maven</groupId>
      <artifactId>rewrite-maven-plugin</artifactId>
      <version>5.2.6</version>
      <configuration>
        <configLocation>rewrite.yml</configLocation>
        <activeRecipes>
          <recipe>com.acme.EverydayHygieneAndCommonsUpgrade</recipe>
        </activeRecipes>
      </configuration>
      <!-- Only if your discover didn't already list these recipes:
      <dependencies>
        <dependency>
          <groupId>org.openrewrite</groupId>
          <artifactId>rewrite-maven</artifactId>
          <version>8.1.6</version>
        </dependency>
      </dependencies>
      -->
    </plugin>
    <!-- keep spring-boot-maven-plugin below, as you already do -->
  </plugins>
</build>
```

## 5) Prime once (faster runs later)

```bash
mvn clean install -DskipTests
```

## 6) Preview (dry run)

```bash
mvn -q rewrite:dryRun
# Patch: target/rewrite/rewrite.patch
```

**What you should see in the patch:**

* `pom.xml`:

  * `commons-lang3` version bumped `3.9` → `3.13.0`
  * `<version>3.5.7</version>` removed from `spring-boot-starter-web`
* `HelloController.java`:

  * `Objects.isNull(name)` → `name == null`
  * import list cleaned, file auto-formatted
  * license header added at top (if you kept that step)

## 7) Apply

Pick one:

```bash
# Let OpenRewrite write files:
mvn -q rewrite:run
```

or:

```bash
git apply --check target/rewrite/rewrite.patch
git apply target/rewrite/rewrite.patch
```

## 8) Verify

```bash
mvn -q -DskipTests=true validate
```

Hit `http://localhost:8080/hello` after a `mvn spring-boot:run` if you want to sanity-check runtime behavior.

---

## 💡 Why this is a great practice run

* **POM upgrade:** realistic example of bumping a library you control (not the parent).
* **Redundant versions:** common cleanup when teams accidentally pin versions the parent already manages.
* **Code modernisation:** removing `Objects.isNull` and normalizing imports/formatting are everyday refactors that keep diffs clean.
* **Composite recipe:** you practice composing multiple built-ins into a single, reviewable change set.

---

### Extras you can tack on (all listed in your `discover`)

* Swap a method name: `org.openrewrite.java.ChangeMethodName`
* Replace a constant: `org.openrewrite.java.ReplaceConstant`
* Add/Remove plugins: `org.openrewrite.maven.AddPlugin`, `RemovePlugin`
* Normalize POM layout: `org.openrewrite.maven.OrderPomElements`
* Enforce import style only: `org.openrewrite.java.OrderImports`, `UseStaticImport` / `NoStaticImport`

### NOTE 
 - use the maven view on lower left side in vscode to view the dependency information like correct `default` version numbers.
 - For example, in this case, the default version for `spring-boot-starter-web` is 3.5.7 as per the maven's depenencies view. 