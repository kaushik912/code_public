```zsh
alias mvn='mvn -T 1C'

export MAVEN_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=100"
MAVEN_OPTS+=" --add-opens=java.base/java.lang=ALL-UNNAMED"
MAVEN_OPTS+=" --add-opens=java.base/java.nio.file=ALL-UNNAMED"
MAVEN_OPTS+=" --add-opens=java.base/sun.nio.fs=ALL-UNNAMED"
MAVEN_OPTS+=" --add-opens=java.base/java.util=ALL-UNNAMED"
MAVEN_OPTS+=" --add-opens=java.base/java.io=ALL-UNNAMED"
```

### Why this helps

**`mvn -T 1C`**

* Enables parallel module builds (1 thread per CPU core)
* Significantly reduces build and OpenRewrite execution time in multi-module projects

**`MAVEN_OPTS`**

* Provides stable JVM memory and GC behavior for large Maven runs
* Adds required `--add-opens` to avoid Java 17 reflective-access failures in Maven plugins and OpenRewrite

