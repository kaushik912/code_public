# Replace System.out with Logger.info - Manual Approach

### Step 1:
Manually add Slf4j Logger to the class (usually at the top).
Otherwise we need to write a imperative recipe.

### Step 2: Add Lombok @Slf4j annotation (optional)
This step simply replaces Logger Declaration with lombok's @Slf4j annotation

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-migrate-java:RELEASE -Drewrite.activeRecipes=org.openrewrite.java.migrate.lombok.log.UseSlf4j -Drewrite.exportDatatables=true  
```

### Step 3: Replace System.out.println with logger

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-logging-frameworks:RELEASE -Drewrite.activeRecipes=org.openrewrite.java.logging.SystemPrintToLogging -Drewrite.exportDatatables=true  
```

Here is where the magic happens! 
The System.out.println() get replaced with logger.info()


## Below works without manual adding logger - Automated

We need to pass addLogger=true with other options and the magic happens!

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-logging-frameworks:RELEASE \
  -Drewrite.activeRecipes="org.openrewrite.java.logging.SystemOutToLogging" \
  -Drewrite.options="addLogger=true,loggerName=log,loggingFramework=SLF4J,level=info"
```

Another way in CLI would be:

```bash
mvn rewrite:run \
  -Drewrite.activeRecipes="org.openrewrite.java.logging.SystemOutToLogging" \
  -DaddLogger=true \
  -DloggerName=log \
  -DloggingFramework=SLF4J \
  -Dlevel=info
```

#### Better to use YAML

It is neat and easy to maintain

```yaml
---
type: specs.openrewrite.org/v1beta/recipe
name: com.yourorg.ReplaceSystemOut
recipeList:
  - org.openrewrite.java.logging.SystemOutToLogging:
      addLogger: true
      loggerName: log
      loggingFramework: SLF4J
      level: info
```