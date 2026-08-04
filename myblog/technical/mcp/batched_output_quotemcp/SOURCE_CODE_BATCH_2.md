# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/randomquote/QuoteTools.java

```java
package com.example.randomquote;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

@Service
public class QuoteTools {

    private final QuoteService quoteService; // your existing service

    public QuoteTools(QuoteService quoteService) {
        this.quoteService = quoteService;
    }

    @Tool(description = "Returns a random inspirational quote")
    public String randomQuote() {
        return quoteService.getRandomQuote();
    }
}
```

---

## File: src/main/java/com/example/randomquote/RandomquoteApplication.java

```java
package com.example.randomquote;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class RandomquoteApplication {

	public static void main(String[] args) {
		SpringApplication.run(RandomquoteApplication.class, args);
	}

	@Bean
	public ToolCallbackProvider quoteToolProvider(QuoteTools quoteTools) {
		return MethodToolCallbackProvider.builder()
				.toolObjects(quoteTools)
				.build();
	}

}
```

---

## File: src/main/resources/application.properties

```
spring.application.name=randomquote
```

---

## File: src/test/java/com/example/randomquote/RandomquoteApplicationTests.java

```java
package com.example.randomquote;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class RandomquoteApplicationTests {

	@Test
	void contextLoads() {
	}

}
```

---

## File: target/classes/application.properties

```
spring.application.name=randomquote
```

---

