# Spring Boot Testing Cheatsheet

Quick reference: what each test annotation is for, when to reach for it, and a snippet.

---

## `@SpringBootTest` — full application context

Loads the entire app (all beans, all config). Use when you need real end-to-end
wiring, not just one layer.

Two flavors:

- **Default (`MOCK` web environment)** — context loads, no real server. Good for
  a cheap "does everything wire up" smoke test.
- **`RANDOM_PORT`** — starts a real embedded server on a random port. Use with
  RestAssured/TestRestTemplate for true HTTP-level integration tests.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProductApiTest {

    @LocalServerPort
    private int port;

    @Test
    void givenProductExists_whenGetCategory_thenReturns200() {
        RestAssured.port = port;

        given()
        .when()
            .get("/products/1/category")
        .then()
            .statusCode(200);
    }
}
```

**Downside**: slow — boots the whole context. Don't reach for this by default;
use it for real request/response contract tests, not unit-level logic.

---

## RestAssured BDD style — `given().when().then()`

RestAssured's own fluent API already reads as Given/When/Then — pair it with
`@SpringBootTest(RANDOM_PORT)` for full-stack API tests. This is the shape to
use for regression tests / contract tests against real endpoints.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProductCategoryTest {

    @LocalServerPort
    private int port;

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
    }

    @Test
    void givenCategorySet_whenGetCategory_thenReturnsUpperCased() {
        // Given: product id=1 seeded with category="electronics"

        // When / Then
        given()
        .when()
            .get("/products/1/category")
        .then()
            .statusCode(200)
            .body(equalTo("ELECTRONICS"));
    }

    @Test
    void givenPostBody_whenCreateProduct_thenReturns201() {
        // Given
        String requestBody = """
            {"name": "Mug", "category": "kitchen"}
            """;

        // When / Then
        given()
            .contentType(ContentType.JSON)
            .body(requestBody)
        .when()
            .post("/products")
        .then()
            .statusCode(201)
            .body("category", equalTo("kitchen"));
    }
}
```

Notes:

- `given()` = request setup (headers, body, auth) — maps to **Given**.
- `.when().get(...)/.post(...)` = the action — maps to **When**.
- `.then().statusCode(...).body(...)` = assertions — maps to **Then**.
- Prefer this over MockMvc when you want a *real* running server and real
  serialization (e.g. verifying Jackson output, not just a mocked service
  return value).
- Keep plain Mockito (`given().willReturn()` is BDDMockito, not RestAssured —
  don't confuse the two) unless the whole test suite already leans BDD-style;
  see the project's testing-style convention.

---

## `@WebMvcTest` — web layer only

Loads only MVC infrastructure (controllers, filters, `@ControllerAdvice`,
Jackson config) — no service/repository beans. You mock collaborators.

Use for: controller routing, request validation, status codes, JSON shape,
exception-handler behavior.

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Test
    void givenServiceReturnsCategory_whenGet_thenReturns200() throws Exception {
        given(productService.getUpperCasedCategory(1L)).willReturn("ELECTRONICS");

        mockMvc.perform(get("/products/1/category"))
            .andExpect(status().isOk())
            .andExpect(content().string("ELECTRONICS"));
    }
}
```

---

## `@DataJpaTest` — repository/JPA layer only

Loads only JPA config + an embedded DB (H2 by default). Each test is
transactional and auto-rolled-back — no manual cleanup needed.

Use for: custom repository queries, entity mapping, cascade behavior.

```java
@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void givenSavedProduct_whenFindById_thenReturnsIt() {
        productRepository.save(new Product(1L, "Mouse", "electronics"));

        assertThat(productRepository.findById(1L)).isPresent();
    }
}
```

**Caveat**: H2 dialect can diverge from real Postgres/MySQL (JSON columns,
case sensitivity, etc). If dialect-specific behavior matters, use
Testcontainers instead.

---

## `@JdbcTest` — plain JDBC layer

Like `@DataJpaTest`, but for raw `JdbcTemplate` usage — no Hibernate/JPA
entities involved.

---

## `@RestClientTest` — outbound HTTP calls

Mocks the server side when your code calls another service via
`RestTemplate`/`RestClient`. Use instead of hitting a real network call.

```java
@RestClientTest(WeatherClient.class)
class WeatherClientTest {

    @Autowired
    private MockRestServiceServer server;

    @Autowired
    private WeatherClient weatherClient;

    @Test
    void givenApiReturnsTemp_whenGetWeather_thenParsesIt() {
        server.expect(requestTo("/weather"))
            .andRespond(withSuccess("{\"temp\":22}", MediaType.APPLICATION_JSON));

        assertThat(weatherClient.getTemp()).isEqualTo(22);
    }
}
```

---

## Plain unit test (no Spring at all)

For pure logic — a service method, a mapper, a validator — skip Spring
entirely. Fastest option, no context startup.

```java
@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    @Test
    void givenNullCategory_whenGetUpperCasedCategory_thenReturnsNull() {
        given(productRepository.findById(1L))
            .willReturn(Optional.of(new Product(1L, "Gift Card", null)));

        assertThat(productService.getUpperCasedCategory(1L)).isNull();
    }
}
```

---

## `@EmbeddedKafka` — Kafka producer/consumer

Spins up a real in-memory Kafka broker (from `spring-kafka-test`) — exercises
real serialization/config without Docker.

```java
@SpringBootTest
@EmbeddedKafka(partitions = 1, topics = "orders")
class OrderProducerTest {

    @Autowired
    private KafkaTemplate<String, Order> kafkaTemplate;

    @Test
    void givenOrder_whenSend_thenPublishedToTopic() {
        kafkaTemplate.send("orders", new Order(1L));
        // consume + assert
    }
}
```

Fall back to Testcontainers only if broker-specific behavior (partitioning,
broker config) matters.

---

## Testcontainers — real infra behavior

Spins up a real Docker container (Postgres, Kafka, Redis, etc). Use when H2 or
embedded fakes diverge too much from production behavior.

```java
@SpringBootTest
@Testcontainers
class ProductRepositoryPostgresTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
    }
}
```

---

## `@WithMockUser` — simulating auth in slice tests

Use inside `@WebMvcTest` to test secured endpoints without a real login flow.

```java
@Test
@WithMockUser(roles = "ADMIN")
void givenAdmin_whenDeleteProduct_thenReturns204() throws Exception {
    mockMvc.perform(delete("/products/1"))
        .andExpect(status().isNoContent());
}
```

---

## Awaitility — testing async/`@Async`/`@Scheduled` code

Polls for a condition instead of `Thread.sleep()` — avoids flaky fixed-delay
tests.

```java
@Test
void givenAsyncJob_whenTriggered_thenEventuallyCompletes() {
    jobService.runAsync();

    await().atMost(5, SECONDS)
        .until(() -> jobService.isComplete());
}
```

---

## Rule of thumb

Pick the **narrowest slice** that exercises what you're testing:

1. Pure logic → plain Mockito unit test
2. One layer (web / data / jdbc) → matching `@...Test` slice
3. Full request → response contract → `@SpringBootTest(RANDOM_PORT)` + RestAssured
4. Infra behavior a fake can't replicate → Testcontainers

## Common pitfalls

- `@SpringBootTest` everywhere → slow suite. Reach for slice tests first.
- `@MockBean`/`@SpyBean` inside `@SpringBootTest` creates a new context per
  unique mock combination → context cache misses → slow CI.
- `@DataJpaTest` auto-rolls-back each test; plain `@SpringBootTest` does
  **not** unless you add `@Transactional` yourself.
- H2 (used by `@DataJpaTest` default) can hide dialect-specific bugs —
  verify against real DB via Testcontainers when it matters.
