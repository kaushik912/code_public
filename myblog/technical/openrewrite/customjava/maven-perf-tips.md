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