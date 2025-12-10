
# Exercise
Implement [StringIsEmpty.java]

Run the recipe using:
```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.StringIsEmptyRecipe
```

## Implementation Details

The `StringIsEmpty` recipe uses Google's Refaster framework to replace verbose string length checks with the more idiomatic `isEmpty()` method.

### What was implemented:

The recipe defines two **before** patterns that should be replaced:
1. **Standard form**: `s.length() == 0`
2. **Reversed form**: `0 == s.length()` (Yoda condition)

And one **after** pattern:
- `s.isEmpty()`

### How it works:

```java
@BeforeTemplate
boolean lengthEqualsZero(String s) {
    return s.length() == 0;
}

@BeforeTemplate
boolean lengthEqualsZeroReversed(String s) {
    return 0 == s.length();
}

@AfterTemplate
boolean isEmpty(String s) {
    return s.isEmpty();
}
```

When the recipe runs, OpenRewrite will:
1. Scan your codebase for any occurrence of the before patterns
2. Replace them with the after pattern
3. Generate a patch file showing the changes

### Testing:
Run the tests to verify the recipe works correctly:
```bash
mvn test
```

All tests in `StringIsEmptyTest` should pass when the recipe is correctly implemented.

## Java 17 Compatibility

If you have a hard requirement to use Java 17 instead of Java 21, you'll need to make the following changes to `pom.xml`:

### 1. Update compiler configuration

Set the Java compiler level to 17 in the `<properties>` section:

```xml
<maven.compiler.release>17</maven.compiler.release>
<maven.compiler.testRelease>17</maven.compiler.testRelease>
```

### 2. Downgrade Error Prone dependency

**Important**: Error Prone version 2.43.0+ requires Java 21. For Java 17 compatibility, downgrade to version 2.42.0:

```xml
<dependency>
    <groupId>com.google.errorprone</groupId>
    <artifactId>error_prone_core</artifactId>
    <version>2.42.0</version>
</dependency>
```

**Why these changes are needed:**
- OpenRewrite and Refaster work with both Java 17 and 21
- The Error Prone compiler plugin version 2.43.0+ dropped Java 17 support
- Using version 2.42.0 ensures build compatibility with Java 17
- Without these changes, you'll encounter build failures on Java 17  

## Performance Optimization Tips

### Faster Maven Execution

Speed up OpenRewrite recipe execution with these optimization techniques:

#### 1. Configure JVM Memory Settings

Add to your `~/.zshrc` (or `~/.bashrc` for bash users):

```bash
export MAVEN_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=100"
```

**What this does:**
- `-Xms512m`: Initial heap size of 512MB
- `-Xmx2g`: Maximum heap size of 2GB (adjust based on your system)
- `-XX:+UseG1GC`: Use G1 garbage collector for better pause times
- `-XX:MaxGCPauseMillis=100`: Target maximum GC pause time of 100ms

#### 2. Enable Parallel Builds

Run Maven with parallel thread execution:

```bash
mvn -T 1C rewrite:run -Drewrite.activeRecipes=com.yourorg.StringIsEmptyRecipe
```

**What this does:**
- `-T 1C`: Use 1 thread per CPU core
- You can also use `-T 4` to specify exact thread count

#### 3. Combined Optimized Command

For maximum speed, combine both optimizations:

```bash
mvn clean -T 1C rewrite:run -Drewrite.activeRecipes=com.yourorg.StringIsEmptyRecipe
```

**Performance Impact:**
- Expect 2-4x faster execution on multi-core systems
- Larger projects benefit more from parallel execution
- Memory settings prevent frequent GC pauses during recipe processing

