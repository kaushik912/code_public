## Security Configuration with JWT and RSA Keys

The `SecurityConfig` class is the core component responsible for configuring JWT-based authentication and authorization:

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    private final RSAPublicKey publicKey;

    public SecurityConfig(RSAPublicKey publicKey) {
        this.publicKey = publicKey;
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();

        converter.setJwtGrantedAuthoritiesConverter(jwt -> {
            List<String> roles = jwt.getClaimAsStringList("roles");
            if (roles == null)
                roles = List.of();

            return roles.stream()
                    .map(role -> new SimpleGrantedAuthority("ROLE_" + role)) // prefix required
                    .collect(Collectors.toList());
        });

        return converter;
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withPublicKey(publicKey).build();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, JwtDecoder jwtDecoder) throws Exception {
        http.csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
                .authorizeHttpRequests()
                .requestMatchers("/token").permitAll()
                .requestMatchers("/admin").hasRole("ADMIN") // restrict to ADMIN role
                .requestMatchers("/user").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
                .and()
                .oauth2ResourceServer()
                .jwt()
                .jwtAuthenticationConverter(jwtAuthenticationConverter());

        return http.build();
    }
}
```

### Key Components

1. **@EnableMethodSecurity Annotation**:
   - Enables method-level security using annotations like `@PreAuthorize`
   - Allows role-based access control at the method level

2. **RSA Public Key Injection**:
   - The public key from `RsaKeyConfig` is injected
   - Used for JWT signature verification

3. **JWT Decoder Configuration**:
   ```java
   @Bean
   public JwtDecoder jwtDecoder() {
       return NimbusJwtDecoder.withPublicKey(publicKey).build();
   }
   ```
   - Creates a `JwtDecoder` that uses the RSA public key to verify token signatures
   - Spring automatically uses this decoder to validate incoming JWTs

4. **JWT Authentication Converter**:
   ```java
   @Bean
   public JwtAuthenticationConverter jwtAuthenticationConverter() {
       JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
       
       converter.setJwtGrantedAuthoritiesConverter(jwt -> {
           List<String> roles = jwt.getClaimAsStringList("roles");
           if (roles == null)
               roles = List.of();
               
           return roles.stream()
                   .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                   .collect(Collectors.toList());
       });
       
       return converter;
   }
   ```
   - Extracts roles from JWT claims and converts them to Spring Security authorities
   - Adds the required `ROLE_` prefix to each role
   - This enables role-based access control using claims from the JWT

5. **Security Filter Chain**:
   ```java
   @Bean
   public SecurityFilterChain filterChain(HttpSecurity http, JwtDecoder jwtDecoder) throws Exception {
       http.csrf().disable()
           .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
           .and()
               .authorizeHttpRequests()
               .requestMatchers("/token").permitAll()
               .requestMatchers("/admin").hasRole("ADMIN")
               .requestMatchers("/user").hasAnyRole("USER", "ADMIN")
               .anyRequest().authenticated()
               .and()
               .oauth2ResourceServer()
               .jwt()
               .jwtAuthenticationConverter(jwtAuthenticationConverter());

       return http.build();
   }
   ```
   - Disables CSRF protection (common for stateless APIs)
   - Sets session creation policy to STATELESS (no sessions, fully JWT-based)
   - Configures URL-based access rules:
     - `/token` endpoint is public (for login)
     - `/admin` endpoint requires ADMIN role
     - `/user` endpoint requires USER or ADMIN role
     - All other endpoints require authentication
   - Configures the application as an OAuth2 resource server using JWT
   - Uses the custom JWT authentication converter

## Role-Based Access Control Implementation

Your application implements role-based access control (RBAC) in two complementary ways:

### 1. URL-Based Authorization

In `SecurityConfig`, URL patterns are restricted based on roles:

```java
.authorizeHttpRequests()
    .requestMatchers("/token").permitAll()
    .requestMatchers("/admin").hasRole("ADMIN")
    .requestMatchers("/user").hasAnyRole("USER", "ADMIN")
    .anyRequest().authenticated()
```

This provides coarse-grained access control at the URL level:
- `/token` is accessible without authentication
- `/admin` requires ADMIN role
- `/user` requires USER or ADMIN role
- Other endpoints require any authenticated user

### 2. Method-Level Authorization

In `RoleController`, the `@PreAuthorize` annotation is used for method-level access control:

```java
@RestController
public class RoleController {

    @GetMapping("/user")
    public String userEndpoint() {
        return "Accessible to USER or ADMIN role";
    }

    @GetMapping("/admin")
    public String adminEndpoint() {
        return "Accessible only to ADMIN role";
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'DEV')")
    @GetMapping("/dev")
    public String onlyDev() {
        return "Accessible to both Dev and admin!";
    }
}
```

Note that:
- For `/user` and `/admin` endpoints, security is enforced by URL patterns in `SecurityConfig`
- The dev endpoint uses method-level security with `@PreAuthorize("hasAnyRole('ADMIN', 'DEV')")`
- Method-level security requires `@EnableMethodSecurity` in the `SecurityConfig` class

## Token Generation with Role Claims

To make role-based security work, the JWT token must include role information. This is implemented in the `JwtTokenProvider` and used by `AuthController`:

```java
// From AuthController.java
@PostMapping("/token")
public ResponseEntity<?> token(@RequestBody AuthRequest authRequest) {
    if ("admin".equals(authRequest.username())) {
        return ResponseEntity.ok(jwtTokenProvider.generateToken("admin", List.of("ADMIN", "USER")));
    } else if ("dev".equals(authRequest.username())) {
        return ResponseEntity.ok(jwtTokenProvider.generateToken("dev", List.of("DEV", "USER")));
    } 
    else {
        return ResponseEntity.ok(jwtTokenProvider.generateToken("user", List.of("USER")));
    }
}
```

And in the token generation method:

```java
// From JwtTokenProvider.java
public String generateToken(String username, List<String> roles) {
    Date now = new Date();
    Date expiry = new Date(now.getTime() + validityInMilliseconds);
    Map<String, Object> claims = new HashMap<>();
    claims.put("roles", roles); // Add roles as claim

    return Jwts.builder()
            .setSubject(username)
            .addClaims(claims)
            .setIssuedAt(now)
            .setExpiration(expiry)
            .signWith(privateKey, SignatureAlgorithm.RS256)
            .compact();
}
```

## Authentication Flow with Role Processing

Here's how the entire authentication flow works with role-based processing:

1. **Token Generation**:
   - User submits username to `/token` endpoint
   - Server assigns roles based on the username
   - Server generates JWT with user roles stored in the "roles" claim
   - Token is signed with the private RSA key

2. **Token Validation & Role Extraction**:
   - Client includes JWT in Authorization header
   - Spring OAuth2 Resource Server filter extracts the token
   - `JwtDecoder` validates token signature using the RSA public key
   - `JwtAuthenticationConverter` extracts roles from token claims
   - Roles are converted to Spring Security authorities with "ROLE_" prefix
   - Spring creates a `JwtAuthenticationToken` with these authorities

3. **Authorization Decision**:
   - For URL-based security, Spring checks if the user's roles match the required roles
   - For method-based security, Spring evaluates `@PreAuthorize` expressions

## Testing Role-Based Access

To test the role-based access, you can use Postman or cURL:

1. **Get an admin token**:
   ```bash
   curl -X POST http://localhost:8080/token -H "Content-Type: application/json" -d '{"username": "admin"}'
   ```
   - This returns a JWT with ADMIN and USER roles

2. **Get a regular user token**:
   ```bash
   curl -X POST http://localhost:8080/token -H "Content-Type: application/json" -d '{"username": "user"}'
   ```
   - This returns a JWT with only USER role

3. **Access the admin endpoint with admin token**:
   ```bash
   curl -X GET http://localhost:8080/admin -H "Authorization: Bearer <admin_token>"
   ```
   - Should succeed (200 OK)

4. **Access the admin endpoint with user token**:
   ```bash
   curl -X GET http://localhost:8080/admin -H "Authorization: Bearer <user_token>"
   ```
   - Should fail (403 Forbidden)

5. **Access the user endpoint with user token**:
   ```bash
   curl -X GET http://localhost:8080/user -H "Authorization: Bearer <user_token>"
   ```
   - Should succeed (200 OK)

6. **Access the dev endpoint with admin token**:
   ```bash
   curl -X GET http://localhost:8080/dev -H "Authorization: Bearer <admin_token>"
   ```
   - Should succeed due to `@PreAuthorize("hasAnyRole('ADMIN', 'DEV')")`

## Security Considerations for Production

For production environments, consider these additional security measures:

1. **Password Validation**:
   - The current implementation doesn't validate passwords
   - Integrate with a user store (database) for proper authentication

2. **Token Expiration**:
   - The current setting uses a 5-minute expiration
   - Adjust based on your security requirements

3. **Role Hierarchies**:
   - Consider implementing role hierarchies if you have complex permission structures
   - Spring Security offers `RoleHierarchy` for this purpose

4. **Key Rotation**:
   - Implement a strategy for rotating RSA keys periodically
   - Consider using a vault system like HashiCorp Vault or AWS KMS

5. **Refresh Tokens**:
   - Consider implementing refresh tokens for longer sessions without compromising security

## Conclusion

The security configuration in your application effectively implements JWT-based authentication with RSA key signing and comprehensive role-based access control. The combination of URL-based and method-level security provides flexible options for protecting resources based on user roles.

This implementation pattern is particularly valuable for microservice architectures, where a centralized authentication service can issue JWTs that other services can independently validate using just the public key.