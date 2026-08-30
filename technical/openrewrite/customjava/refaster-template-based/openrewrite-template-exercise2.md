# Exercise 2: UseIntegerValueOf Template Recipe

Implement [UseIntegerValueOfTemplate.java](../src/main/java/com/yourorg/UseIntegerValueOfTemplate.java)

Run the recipe using:
```bash
mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOfTemplateRecipe
```

Or for a dry run to preview changes:
```bash
mvn rewrite:dryRun -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOfTemplateRecipe
```

## Implementation Details

The `UseIntegerValueOfTemplate` recipe demonstrates an **advanced Refaster pattern** for handling method overloads using **nested static classes**. This replaces deprecated `new Integer()` constructors with modern alternatives.

### What was implemented:

This recipe handles two distinct transformations:
1. **Integer from int**: `new Integer(42)` → `Integer.valueOf(42)`
2. **Integer from String**: `new Integer("42")` → `Integer.parseInt("42")`

### Why Nested Classes Pattern?

**The Problem:**
You cannot have two `@BeforeTemplate` methods with different parameter types in the same class because Refaster needs to generate distinct recipes for each pattern. Trying to handle both cases in one class leads to ambiguity.

**The Solution:**
Use **nested static classes** where each class represents one distinct recipe:

```java
@RecipeDescriptor(
    name = "UseIntegerValueOf",
    description = "Use Integer.valueOf(x) or Integer.parseInt(x) instead of new Integer(x)"
)
public class UseIntegerValueOfTemplate {

    // Separate recipe for int case
    public static class IntCase {
        @BeforeTemplate
        Integer before(int x) {
            return new Integer(x);
        }

        @AfterTemplate
        Integer after(int x) {
            return Integer.valueOf(x);
        }
    }

    // Separate recipe for String case
    public static class StringCase {
        @BeforeTemplate
        Integer before(String x) {
            return new Integer(x);
        }

        @AfterTemplate
        Integer after(String x) {
            return Integer.parseInt(x);
        }
    }
}
```

### How It Works:

1. **Outer class** (`UseIntegerValueOfTemplate`):
   - Acts as a container/parent recipe
   - Groups related transformations together
   - Has its own `@RecipeDescriptor` for documentation

2. **Inner static classes** (`IntCase`, `StringCase`):
   - Each becomes a **separate, independent recipe**
   - Each can have its own `@RecipeDescriptor`
   - Type signatures are completely isolated
   - No confusion between overloaded methods

3. **OpenRewrite compilation**:
   - Generates two distinct recipes at compile time:
     - `UseIntegerValueOfTemplate$IntCase`
     - `UseIntegerValueOfTemplate$StringCase`
   - The parent recipe combines both as sub-recipes

### Why This Works Better Than Imperative Approach:

| Aspect | Template (Refaster) | Imperative (Visitor) |
|--------|---------------------|----------------------|
| **Code simplicity** | ~47 lines (including docs) | ~92 lines |
| **Type safety** | Enforced by method signatures | Manual type checking required |
| **Maintenance** | Declarative (what, not how) | Procedural (how, not what) |
| **Constructor detection** | Automatic by parameter type | Manual check of `getConstructorType()` |
| **Multiple overloads** | Nested classes (clean separation) | Complex if/else logic |
| **Generated code** | Optimized by Refaster compiler | Hand-written visitor logic |

**Key Insight:** For straightforward before/after patterns with different signatures, nested template classes are cleaner than writing visitor logic to distinguish between overloads.

### When to Use Nested Template Classes:

✅ **Use this pattern when:**
- You need to handle multiple overloads of the same method/constructor
- Each overload has a distinct transformation
- The transformation is a simple before/after pattern
- You want type safety enforced by Java's type system

❌ **Avoid this pattern when:**
- You need conditional logic beyond type matching
- The transformation requires analyzing surrounding code
- You need to make changes across multiple statements
- You need access to type information beyond method signatures

### Pattern Variations:

**Multiple nested classes for related patterns:**
```java
public class CollectionFactoryMethods {
    public static class ListCase {
        @BeforeTemplate List<String> before() { return new ArrayList<>(); }
        @AfterTemplate List<String> after() { return List.of(); }
    }

    public static class SetCase {
        @BeforeTemplate Set<String> before() { return new HashSet<>(); }
        @AfterTemplate Set<String> after() { return Set.of(); }
    }
}
```

**Multiple before templates for one after (common pattern):**
```java
public static class StringCase {
    @BeforeTemplate
    Integer beforeNew(String x) {
        return new Integer(x);
    }

    @BeforeTemplate
    Integer beforeValueOf(String x) {
        return Integer.valueOf(x);  // Also convert this to parseInt
    }

    @AfterTemplate
    Integer after(String x) {
        return Integer.parseInt(x);
    }
}
```

### Testing:

Run the tests to verify the recipe works correctly:
```bash
mvn test -Dtest=UseIntegerValueOfTest
```

**Note:** The imperative `UseIntegerValueOf` recipe and the template `UseIntegerValueOfTemplate` recipe achieve the same result. Compare both implementations to understand the trade-offs!

### Comparison: Template vs Imperative

Both approaches are included in this project:

| File | Approach | Lines of Code | Best For |
|------|----------|---------------|----------|
| `UseIntegerValueOf.java` | Imperative Visitor | ~92 | Complex logic, multiple files |
| `UseIntegerValueOfTemplate.java` | Refaster Template | ~47 | Simple patterns, type-based |

**Real-world guidance:**
- Start with templates for simple cases
- Switch to imperative when you need:
  - Access to parent/sibling nodes
  - Conditional transformations beyond type matching
  - Multi-statement transformations
  - Import management complexity

### Generated Recipe Names

When compiled, this template generates:
- Parent: `com.yourorg.UseIntegerValueOfTemplateRecipe`
- Child 1: `com.yourorg.UseIntegerValueOfTemplate$IntCaseRecipe`
- Child 2: `com.yourorg.UseIntegerValueOfTemplate$StringCaseRecipe`

You can run them individually:
```bash
# Run only the int case
mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOfTemplate\$IntCaseRecipe

# Run only the String case
mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOfTemplate\$StringCaseRecipe

# Run both (via parent)
mvn rewrite:run -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOfTemplateRecipe
```

---

## Key Takeaway

**Nested static classes in Refaster templates** provide a clean, type-safe way to handle method/constructor overloads. Each nested class becomes an independent recipe with its own distinct type signature, eliminating the ambiguity and complexity of handling multiple overloads in a single visitor implementation.