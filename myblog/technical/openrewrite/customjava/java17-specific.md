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