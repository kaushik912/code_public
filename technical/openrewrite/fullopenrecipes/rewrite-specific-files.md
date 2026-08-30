### Filtering files with Maven's includes configuration

When using the **Maven plugin**, OpenRewrite operates on the Maven module’s source sets (`src/main/java` and `src/test/java`) by default — there’s no `-Drewrite.files` equivalent.

However, you can restrict what Maven exposes to the plugin using build configuration like this:

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>6.22.1</version>
  <configuration>
    <activeRecipes>
      <recipe>org.openrewrite.staticanalysis.RemoveUnusedLocalVariables</recipe>
    </activeRecipes>
    <includes>
      <include>src/main/java/com/example/helloworld/staticanalysis/**/*.java</include>
    </includes>
  </configuration>
</plugin>
```

This limits the rewrite operation to files in that path.

Then run:

```bash
mvn rewrite:run
```
