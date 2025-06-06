# What are Public and Private Keys? (Simple Explanation)

Imagine you have a **locked mailbox** with two keys:

* **Private key:** Only you have this key. You use it to **lock** the mailbox.
* **Public key:** You give copies of this key to your friends. They can use it to **open** the mailbox and check if it was really you who locked it.

---

### In cryptography terms:

* The **private key** is **secret** and used to **sign** data (like a JWT token).
* The **public key** is **public** and used to **verify** that the data was signed with the matching private key.

No one can fake your signature without the private key, but anyone with the public key can check the signature is valid.

---

### Why is this useful for JWT?

When your authentication server creates a token:

* It **signs** the token with the **private key** — proving it came from your server.
* Any service receiving the token can **verify** it using the **public key** — no need to share the private key.

---

# Step-by-Step Explanation of the Code

---

### 1. **Generating RSA Keys**

```bash
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

* **Why?** We need a private key to sign JWT tokens, and a public key to verify tokens.
* **What?** Creates two files: one private (keep secret), one public (share safely).

---

### 2. **Loading Keys in Java**

```java
public static PrivateKey getPrivateKey(String filename) {...}
public static PublicKey getPublicKey(String filename) {...}
```

* **Why?** Java needs to load keys from PEM files into usable objects.
* **What?** Reads files, removes headers/footers, decodes Base64, converts to key objects.

---

### 3. **Creating JWT Token Provider**

```java
public class JwtTokenProvider {
  private final PrivateKey privateKey;
  private final PublicKey publicKey;
  ...
  public String createToken(String username) {...}
  public boolean validateToken(String token) {...}
  public String getUsername(String token) {...}
}
```

* **Why?** This class manages token creation and validation.
* **Creating token:** Signs with private key (only your server can do this).
* **Validating token:** Verifies signature with public key (anyone can do this).
* **Get username:** Extracts info stored inside token.

---

### 4. **Security Configuration**

```java
http
  .authorizeHttpRequests(auth -> auth
    .requestMatchers("/token").permitAll()
    .anyRequest().authenticated())
  .addFilterBefore(new JwtTokenFilter(jwtTokenProvider), UsernamePasswordAuthenticationFilter.class);
```

* **Why?** Secure the app so `/token` is public (login endpoint), and all other requests require a valid JWT.
* **Filter:** Every incoming request (except `/token`) checks for JWT in header and validates it.

---

### 5. **JWT Token Filter**

```java
protected void doFilterInternal(...) {
  String authHeader = request.getHeader("Authorization");
  if (authHeader != null && authHeader.startsWith("Bearer ")) {
    String token = authHeader.substring(7);
    if (jwtTokenProvider.validateToken(token)) {
      String username = jwtTokenProvider.getUsername(token);
      // Set authenticated user in Spring Security context
    }
  }
  chain.doFilter(request, response);
}
```

* **Why?** This intercepts requests to:

  * Extract the JWT token from header.
  * Validate it using the public key.
  * If valid, mark the user as authenticated.
* If token is invalid or missing → request fails with 401 (unauthorized).

---

### 6. **Auth Controller**

```java
@PostMapping("/token")
public ResponseEntity<?> token(...) {
  // Check username/password
  // If valid, create and return JWT token signed with private key
}

@GetMapping("/profile")
public ResponseEntity<?> profile() {
  // Returns protected info, only if JWT token valid
}
```

* **Why?**

  * `/token` lets users login and get JWT tokens.
  * `/profile` is protected; users need a valid JWT token to access.

---

### 7. **App Startup**

```java
@Bean
public JwtTokenProvider jwtTokenProvider() throws Exception {
  PrivateKey privateKey = KeyUtil.getPrivateKey("private_key.pem");
  PublicKey publicKey = KeyUtil.getPublicKey("public_key.pem");
  return new JwtTokenProvider(privateKey, publicKey);
}
```

* **Why?** Loads your keys once at startup and creates a `JwtTokenProvider` bean used in other parts.
* **What?** This wiring enables your app to sign and verify tokens securely.

---

# Summary in Super Simple Terms

| Step                           | What happens                        | Why it matters                    |
| ------------------------------ | ----------------------------------- | --------------------------------- |
| Generate RSA keys              | Create private & public keys        | Private key signs tokens securely |
| Load keys in Java              | Read keys from files                | To use keys in the app            |
| Create token with private key  | Server issues signed JWT token      | Token proves identity             |
| Validate token with public key | Check token authenticity            | Anyone can verify token           |
| Secure endpoints               | Protect API with JWT authentication | Only authorized users access data |
| Filter incoming requests       | Extract and verify JWT              | Authenticate every request        |

---


