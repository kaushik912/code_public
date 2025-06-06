Sure! Here's a **simple, complete example** showing how to:

1. Define an environment variable like `IS_TEST_MODE`,
2. Inject it into a Spring Boot application using `@Value`,
3. Return it from a REST API.

---

## ✅ Step-by-Step Example

### 🔧 Step 1: Set the Environment Variable

You can set it in your system or run your app like:

```bash
export IS_TEST_MODE=true
```

Or if running via command line:

```bash
java -DIS_TEST_MODE=true -jar your-app.jar
```

Or using Spring Boot's built-in support:

```bash
java -jar your-app.jar --IS_TEST_MODE=true
```

---

### 📁 Step 2: Add Code to Read and Print the Variable

```java
package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/env")
public class EnvController {

    @Value("${IS_TEST_MODE:false}") // fallback to false if not set
    private String isTestMode;

    @GetMapping
    public String getTestMode() {
        return "Is Test Mode: " + isTestMode;
    }
}
```

---

### 🧪 Example Response

Call the API:

```
GET http://localhost:8080/env
```

**If IS\_TEST\_MODE=true was set**, you'll get:

```
Is Test Mode: true
```

**If not set**, you'll get:

```
Is Test Mode: false
```

---

### 📁 Optional: Add to `application.properties`

You can also define a default inside `src/main/resources/application.properties`:

```properties
IS_TEST_MODE=false
```

Environment variables or command-line args will **override** this.

---

### 🧠 Tip

To inject as a boolean instead of a string:

```java
@Value("${IS_TEST_MODE:false}")
private boolean isTestMode;
```

Then return it like:

```java
return "Is Test Mode: " + isTestMode;
```

## My note

I was able to verify using export. Below are the simple steps that I tried: 

- export IS_TEST_MODE=true
- mvn spring-boot:run
- curl http://localhost:8080/env
> Output Seen: Is Test Mode: true

## Follow-up thoughts
- As we can see here, we could store sensitive secrets in an environment variable and avoid hard-coding it in our code.
