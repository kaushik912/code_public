# Implementing UseIntegerValueOf: An OpenRewrite Recipe Guide

This guide explains the implementation of `UseIntegerValueOf.java`, which replaces deprecated `new Integer(x)` constructor calls with modern alternatives (`Integer.valueOf()` or `Integer.parseInt()`).

Note: A sample code for `UseIntegerValueOf.java` is present in `recipes` folder.

## Implementation Overview

The recipe transforms:
- `new Integer(42)` → `Integer.valueOf(42)` (for int arguments)
- `new Integer("42")` → `Integer.parseInt("42")` (for String arguments)

**File:** `src/main/java/com/yourorg/UseIntegerValueOf.java`

## Key Patterns Used

### 1. Recipe Class Structure

```java
@Value
@EqualsAndHashCode(callSuper = false)
public class UseIntegerValueOf extends Recipe {
    // Implementation
}
```

**Why this pattern:**
- `@Value`: Makes the recipe immutable (required for thread safety and idempotence)
- `@EqualsAndHashCode(callSuper = false)`: Ensures proper equality comparison for recipe serialization
- Extends `Recipe`: Standard base class for all OpenRewrite transformations

### 2. JavaVisitor (Not JavaIsoVisitor)

```java
return new JavaVisitor<ExecutionContext>() {
    @Override
    public J visitNewClass(J.NewClass newClass, ExecutionContext ctx) {
        J.NewClass n = (J.NewClass) super.visitNewClass(newClass, ctx);
        // ...
    }
};
```

**Why JavaVisitor:**
- We need to replace `NewClass` nodes with `MethodInvocation` nodes (different types)
- JavaIsoVisitor requires returning the same type
- JavaVisitor allows returning any `J` tree element

**Alternative considered:** JavaIsoVisitor would cause a ClassCastException when returning a MethodInvocation from visitNewClass.

### 3. Constructor Type Checking (Critical Pattern)

```java
if (n.getConstructorType() != null) {
    List<JavaType> parameterTypes = n.getConstructorType().getParameterTypes();
    if (!parameterTypes.isEmpty()) {
        JavaType paramType = parameterTypes.get(0);

        if (paramType instanceof JavaType.Primitive) {
            // Integer(int) → valueOf
        } else if (paramType instanceof JavaType.Class) {
            // Integer(String) → parseInt
        }
    }
}
```

**Why this approach:**
- `getConstructorType()` gives us the actual constructor signature being invoked
- Checking `parameterTypes` is more reliable than checking argument types
- String literals might not have full type information, but constructor types always do

**Failed approach:** Initially tried checking `arg.getType()` which failed for string literals.

### 4. JavaTemplate for Code Generation

```java
private final JavaTemplate valueOfTemplate =
    JavaTemplate.builder("Integer.valueOf(#{any(int)})").build();

private final JavaTemplate parseIntTemplate =
    JavaTemplate.builder("Integer.parseInt(#{any(String)})").build();

// Application:
return valueOfTemplate.apply(getCursor(), n.getCoordinates().replace(), arg);
```

**Why this pattern:**
- `#{any(Type)}`: Type-safe insertion point that preserves code formatting
- `getCursor()`: Provides context for the transformation
- `getCoordinates().replace()`: Specifies we're replacing the entire NewClass node
- Declared as final fields: Templates are immutable and reusable

### 5. Type Safety and Null Checking

```java
if (n.getClazz() != null && n.getClazz().getType() != null) {
    JavaType.FullyQualified type = (JavaType.FullyQualified) n.getClazz().getType();
    if (type.getFullyQualifiedName().equals("java.lang.Integer")) {
        // Safe to proceed
    }
}
```

**Why defensive checks:**
- AST nodes can have null types during parsing errors
- Only transform when we're certain it's an Integer constructor
- Prevents false positives on other constructors

## Common Recipe Patterns Reference

### Pattern 1: Simple Method Replacement

Use when replacing one method call with another (like Guava → Java Collections):

```java
private static final MethodMatcher OLD_METHOD =
    new MethodMatcher("com.package.Class methodName(..)");

@Override
public J visitMethodInvocation(J.MethodInvocation method, ExecutionContext ctx) {
    if (OLD_METHOD.matches(method)) {
        maybeRemoveImport("com.package.Class");
        maybeAddImport("new.package.NewClass");
        return template.apply(getCursor(), method.getCoordinates().replace(), ...);
    }
    return super.visitMethodInvocation(method, ctx);
}
```

**Example:** NoGuavaListsNewArrayList.java

### Pattern 2: Preconditions for Performance

Use to avoid scanning files that don't need transformation:

```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor() {
    return Preconditions.check(
        new UsesMethod<>(METHOD_MATCHER),
        new JavaVisitor<ExecutionContext>() { /* implementation */ }
    );
}
```

**Example:** NoGuavaListsNewArrayList.java, AssertEqualsToAssertThat.java

### Pattern 3: Refaster Templates (Simplest Approach)

Use for straightforward before/after patterns:

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

**Example:** SimplifyTernary.java

## Design Decisions

### Decision 1: No Preconditions

**Considered:** Adding `Preconditions.check(new UsesType<>("java.lang.Integer", null), visitor)`

**Chose:** Skip preconditions

**Reasoning:**
- Integer is ubiquitous in Java code
- The overhead of checking every file is minimal
- Constructor calls are relatively rare, so visitor overhead is low

### Decision 2: Return Type Strategy

**Considered:** Using JavaIsoVisitor with type casting

**Chose:** JavaVisitor returning `J` instead of `J.NewClass`

**Reasoning:**
- JavaTemplate.apply() returns a MethodInvocation, not NewClass
- Attempting to cast would cause ClassCastException
- JavaVisitor's flexibility allows heterogeneous return types

### Decision 3: Type Detection Strategy

**Evolution:**
1. ❌ Check `arg.getType()` - Failed for String literals
2. ❌ Check `arg instanceof J.Literal` - Incomplete solution
3. ✅ Check `n.getConstructorType().getParameterTypes()` - Reliable solution

**Final choice reasoning:**
- Constructor signatures are always fully typed
- Works for both literals and variable references
- Single source of truth for which constructor is invoked

## Testing Strategy

The recipe includes two test cases:

```java
@Test
void replacesNewIntegerWithValueOf() {
    // new Integer(42) → Integer.valueOf(42)
}

@Test
void replacesNewIntegerWithParseInt() {
    // new Integer("42") → Integer.parseInt("42")
}
```

**Key insight:** Test both overloads to ensure constructor signature detection works correctly.

## Comparison: When to Use Each Approach

| Approach | Use When | Example Recipe |
|----------|----------|----------------|
| **Refaster Template** | Simple 1:1 code replacement | SimplifyTernary |
| **MethodMatcher + Visitor** | Replacing method calls | NoGuavaListsNewArrayList |
| **Custom Visitor Logic** | Complex transformations, type changes | UseIntegerValueOf |
| **Trait Matchers** | High-level semantic matching | FindSpringBeans |
| **Preconditions** | Optimization for rarely-used APIs | NoGuavaListsNewArrayList |

## Further Reading

- **Method Patterns:** https://docs.openrewrite.org/reference/method-patterns
- **JavaTemplate:** https://docs.openrewrite.org/concepts-and-explanations/javatemplate
- **LST (Lossless Semantic Tree):** Understanding OpenRewrite's AST representation

## Quick Reference Checklist

When implementing a recipe:

- [ ] Use `@Value` and `@EqualsAndHashCode(callSuper = false)`
- [ ] Implement `getDisplayName()` and `getDescription()`
- [ ] Choose appropriate visitor type (JavaVisitor vs JavaIsoVisitor)
- [ ] Create JavaTemplate instances as final fields
- [ ] Use null-safe type checking
- [ ] Call `maybeAddImport()` / `maybeRemoveImport()` when changing types
- [ ] Consider preconditions for performance
- [ ] Write comprehensive tests covering edge cases
- [ ] Return new visitor instances from `getVisitor()` (avoid state leakage)

---

## Running the Recipe

```bash
# Run the recipe
export MAVEN_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=100"
mvn -T 1C rewrite:dryRun -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOf

# Or with Gradle
./gradlew rewriteDryRun -Drewrite.activeRecipes=com.yourorg.UseIntegerValueOf
```
