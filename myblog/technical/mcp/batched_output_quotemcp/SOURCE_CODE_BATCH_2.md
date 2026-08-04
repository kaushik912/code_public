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

## File: src/test/java/com/example/randomquote/QuoteMcpTester.java

```java
package com.example.randomquote;

import io.modelcontextprotocol.client.McpClient;
import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.client.transport.HttpClientSseClientTransport;
import io.modelcontextprotocol.spec.McpSchema.CallToolRequest;
import io.modelcontextprotocol.spec.McpSchema.CallToolResult;
import io.modelcontextprotocol.spec.McpSchema.ListToolsResult;

import java.time.Duration;
import java.util.Map;

/**
 * Scratch MCP client — Option A, no LLM.
 *
 * PREREQ: the app must already be running (e.g. `./mvnw spring-boot:run`) — the
 * same instance Claude talks to on port 8080. This just plays the role of an MCP
 * client and drives the tool by name.
 *
 * Run it: right-click -> Run 'QuoteMcpTester.main()' in your IDE.
 *
 * Tweak the three knobs below to experiment with different tools / args.
 */
public class QuoteMcpTester {

    // --- knobs to change while experimenting -------------------------------
    private static final String SERVER_BASE_URL = "http://localhost:8080"; // "/sse" is the default endpoint
    private static final String TOOL_NAME       = "randomQuote";
    private static final Map<String, Object> ARGS = Map.of(); // e.g. Map.of("category", "tech")
    // -----------------------------------------------------------------------

    public static void main(String[] args) {
        var transport = HttpClientSseClientTransport
                .builder(SERVER_BASE_URL)
                .build();

        try (McpSyncClient client = McpClient.sync(transport)
                .requestTimeout(Duration.ofSeconds(10))
                .build()) {

            client.initialize(); // handshake

            // tools/list — see what the server advertises
            ListToolsResult tools = client.listTools();
            System.out.println("Available tools:");
            tools.tools().forEach(t -> System.out.println("  - " + t.name() + " : " + t.description()));

            // tools/call — invoke the tool
            CallToolResult result = client.callTool(new CallToolRequest(TOOL_NAME, ARGS));
            System.out.println("\nCall '" + TOOL_NAME + "' " + ARGS);
            System.out.println("  isError = " + result.isError());
            System.out.println("  content = " + result.content());
        }
    }
}
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

