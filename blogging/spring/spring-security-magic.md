## Overview: What happens when you call `/profile` with a token

1. **Spring Security filter chain intercepts the HTTP request** before your controller method is invoked.

2. It checks the request’s **Authorization header** for a Bearer token.

3. If a token is present, it tries to **validate the JWT** using the configured `JwtDecoder`.

4. If validation succeeds, it extracts user details and **sets the SecurityContext with an authenticated principal**.

5. Your controller method runs (since the request is authenticated).

6. If validation fails or token is missing, Spring Security **returns 401 Unauthorized** automatically.

---

## How this works in your app step-by-step

### 1. Security filter chain and configuration

In your `SecurityConfig`:

```java
http
  .csrf().disable()
  .authorizeHttpRequests(auth -> auth
      .requestMatchers("/token").permitAll()  // Allow token endpoint without auth
      .anyRequest().authenticated()           // All others require authentication
  )
  .oauth2ResourceServer(oauth -> oauth.jwt()); // Enable JWT-based resource server support
```

* `oauth2ResourceServer(oauth -> oauth.jwt())` **registers a JWT authentication filter** (`JwtAuthenticationFilter`) in the Spring Security filter chain.
* This filter listens to every incoming request (except excluded paths).

---

### 2. The JWT Authentication Filter (`JwtAuthenticationFilter`)

* This filter looks for an **Authorization header** starting with `Bearer `.
* If present, it extracts the token string.

---

### 3. Token decoding and validation

* The filter uses your configured `JwtDecoder` bean (in your case, `NimbusJwtDecoder.withSecretKey(secretKey)`).
* The decoder:

  * Parses the JWT,
  * Verifies the signature using your secret key,
  * Checks standard claims (like expiration, issuedAt),
  * Throws exceptions if token is invalid (signature fails, expired, malformed, etc).

---

### 4. Authentication and SecurityContext

* If the token is valid, the filter creates an `Authentication` object (e.g., `JwtAuthenticationToken`), holding details extracted from the token (like username, roles, claims).
* It stores this `Authentication` in the **`SecurityContextHolder`**, which represents the current authenticated user context.
* After this, the request proceeds to your controller methods **as an authenticated request**.

---

### 5. Accessing `/profile`

* Your controller method annotated with `@GetMapping("/profile")` runs.
* You can access the user info from the JWT claims if needed.
* Returns your secured user info JSON response.

---

### 6. If token is missing or invalid

* The JWT filter throws an exception.
* Spring Security’s `ExceptionTranslationFilter` catches it.
* It responds with **HTTP 401 Unauthorized** automatically.
* The request does **not reach your controller**.

---

## Summary Flow Diagram

```
HTTP Request /profile
        ↓
[Spring Security Filter Chain]
        ↓
[JwtAuthenticationFilter]
    - Extract Bearer token
    - Decode & validate token
    - If valid → set SecurityContext
    - If invalid/missing → 401 Unauthorized
        ↓
[Controller method executes]
        ↓
Return secured data
```

---

## How to verify this yourself?

* Pass a **valid token** in Postman `Authorization: Bearer <token>` header → You get **200 OK** with your data.
* Pass an **invalid token** (e.g., wrong signature, expired) → You get **401 Unauthorized**.
* Pass **no token** → Also **401 Unauthorized**.

---


