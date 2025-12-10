
## Better Abstractions: Don't Memorize Details

**1. Use Pre-built Recipes**

Most of the time, you don't need to write code at all. You identify the desired recipe in the OpenRewrite recipe catalog, find its fully qualified name, and configure it in YAML. For example:

```yaml
---
type: specs.openrewrite.org/v1beta/recipe
name: my.custom.Recipe
recipeList:
  - org.openrewrite.java.RemoveAnnotation:
      annotationPattern: '@java.lang.SuppressWarnings("deprecation")'
  - org.openrewrite.java.ChangePackage:
      oldPackageName: com.old
      newPackageName: com.new
```

No complex code needed!

**2. Refaster Templates (Way Simpler)**

Instead of writing visitors and complex logic, you use `@BeforeTemplate` and `@AfterTemplate` annotations. You show an example of code you want to find, and code you want to replace it with:

```java
public class StringIsEmpty {
    @BeforeTemplate
    boolean before(String string) {
        return string.equals("");  // Find this pattern
    }

    @AfterTemplate
    boolean after(String string) {
        return string.isEmpty();   // Replace with this
    }
}
```

That's it! OpenRewrite automatically generates the visitor logic for you. No need to understand LSTs, Cursors, or JavaTemplate syntax.

**3. Recipe Composition (The Decorator Idea)**

You compose simpler recipes together to build complex transformations. Rather than memorizing every nuance, you just chain existing recipes that each do one thing well.

## When to Use Each

- **YAML recipes**: Just combining existing recipes → use this 80% of the time
- **Refaster templates**: Pattern-based replacements (method calls, ternaries, etc.) → use this for simple transformations
- **Imperative recipes**: Complex logic that doesn't fit the patterns above → only when necessary

## The Real Answer

The imperative recipe approach has a very steep learning curve due to the comprehensive API. Most developers shouldn't need to memorize all those details. Instead:

1. Start with the recipe catalog—check if what you need already exists
2. If not, try Refaster templates
3. Only write imperative code if you really need conditional logic or complex tree manipulation
