# Setting Up Spring Boot OAuth2 Authorization Server

This guide walks through creating a JWT-based authentication server with Spring Boot.

## Step 1: Create a skeleton project using Spring Initializr

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,security,oauth2-authorization-server \
  -d type=maven-project \
  -d language=java \
  -d name=auth-server \
  -d packageName=com.example.auth \
  -d javaVersion=17 \
  -o auth-server.zip && unzip auth-server.zip -d auth-server
```

## Step 2: Add JWT dependencies to pom.xml

Add these dependencies to enable JWT token handling:

```xml
<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  <dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.11.5</version>
  </dependency>
  <dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
  </dependency>
  <dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
  </dependency>
</dependencies>
```

## Step 3: Create main application components

### 3.1 Create the Security Configuration

Create SecurityConfig.java class to:
- Configure protected endpoints
- Setup JWT decoder
- Define security rules

```java
package com.example.auth.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;

import javax.crypto.SecretKey;

@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    private final SecretKey secretKey;

    @Autowired
    public SecurityConfig(SecretKey secretKey) {
        this.secretKey = secretKey;
    }
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/token").permitAll() // Public endpoint for token generation
                .anyRequest().authenticated()          // All other endpoints require authentication
            )
            .oauth2ResourceServer(oauth -> oauth.jwt()); // Enable JWT authentication

        return http.build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        // Configure JWT decoder with your secret key
        return NimbusJwtDecoder.withSecretKey(secretKey).build();
    }
}
```

### 3.2 Create a JWT Secret Configuration

Create JWTSecretConfig.java to manage the JWT secret key:

```java
package com.example.auth.config;

import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.crypto.SecretKey;
import java.util.Base64;

@Configuration
public class JWTSecretConfig {

    @Value("${jwt.secret}")
    private String base64Secret;

    @Bean
    public SecretKey jwtSecretKey() {
        return Keys.hmacShaKeyFor(Base64.getDecoder().decode(base64Secret));
    }
}
```

Also create application.properties with your JWT secret:

```properties
spring.application.name=auth-server
jwt.secret=<secret_key_generated_using_key_generator>
```

### 3.3 Create a utility class to generate a secure key

Add KeyGenerator.java to generate a secure key:

```java
package com.example.auth.util;

import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.util.Base64;

public class KeyGenerator {
    public static void main(String[] args) {
        byte[] key = Keys.secretKeyFor(SignatureAlgorithm.HS256).getEncoded();
        System.out.println("Random Key Generated: " + Base64.getEncoder().encodeToString(key));
    }
}
```

Run this class to generate a random secure key for your JWT tokens. You should copy the output and paste it into your application.properties file as the `jwt.secret` value.

### 3.4 Create the Authentication Request model

Create AuthRequest.java to handle login requests:

```java
package com.example.auth.model;

public class AuthRequest {
    private String username;
    private String password;
    
    // Default constructor needed for JSON deserialization
    public AuthRequest() {}
    
    public AuthRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }
    
    // Getters and setters
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
}
```

### 3.5 Create the Token Controller

Create TokenController.java to handle token generation:

```java
package com.example.auth.controller;

import io.jsonwebtoken.Jwts;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.auth.model.AuthRequest;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.Map;

@RestController
public class TokenController {

    private final SecretKey secretKey;

    @Autowired
    public TokenController(SecretKey secretKey) {
        this.secretKey = secretKey;
    }

    @PostMapping("/token")
    public ResponseEntity<?> getToken(@RequestBody AuthRequest request) {
        // For demo purposes, we're using hardcoded credentials
        // In a real application, you'd validate against a user database
        if ("user".equals(request.getUsername()) && "password".equals(request.getPassword())) {
            String token = Jwts.builder()
                    .setSubject(request.getUsername())
                    .claim("email", "user@example.com")
                    .claim("phone", "1234567890")
                    .setIssuedAt(new Date())
                    .setExpiration(new Date(System.currentTimeMillis() + 5 * 60 * 1000)) // 5 mins
                    .signWith(secretKey)
                    .compact();

            return ResponseEntity.ok(Map.of("token", token));
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid credentials");
        }
    }
}
```

### 3.6 Create protected User Controller

Create UserController.java with protected endpoints:

```java
package com.example.auth.controller;

import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/user")
public class UserController {

    @GetMapping("/profile")
    public Map<String, Object> getProfile(@AuthenticationPrincipal Jwt jwt) {
        // Return data extracted from the JWT
        return Map.of(
                "username", jwt.getSubject(),
                "email", jwt.getClaimAsString("email"),
                "phone", jwt.getClaimAsString("phone")
        );
    }
}
```

### 3.7 Create main application class

Ensure your AuthServerApplication.java looks like this:

```java
package com.example.auth;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AuthServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(AuthServerApplication.class, args);
    }
}
```

## Step 4: Test the application

### 4.1 Start the application

Run the application using Maven wrapper:

```bash
./mvnw spring-boot:run
```

The application will start on port 8080 (default).

### 4.2 Test with Postman

Use the included Postman collection:

#### 4.2.1 Get a JWT token

Send a POST request to `http://localhost:8080/token` with body:

```json
{
  "username": "user",
  "password": "password"
}
```

You should receive a response like:

```json
{
  "token": "<someJWTtoken>"
}
```

#### 4.2.2 Access protected endpoint

Send a GET request to `http://localhost:8080/user/profile` with header:
- `Authorization: Bearer <your_token>`

You should receive:

```json
{
  "username": "user",
  "email": "user@example.com",
  "phone": "1234567890"
}
```

### 4.3 Testing Flow Summary:

1. Start the application: `./mvnw spring-boot:run`
2. Import the Postman collection
3. Execute the "Get Token" request
4. Copy the token from the response
5. Use the token in the "Access Protected API" request

## Step 5: Understand the Authentication Flow

For a detailed explanation of how Spring Security and JWT authentication work together in this application, see Spring_Security_Notes.md.

### Authentication Flow Overview:

1. Client sends credentials (username/password) to `/token` endpoint
2. Server validates credentials and generates a signed JWT token
3. Client stores the token and sends it in the Authorization header for subsequent requests
4. Server validates the token signature and expiration for each protected request
5. If valid, the server extracts user information from claims and processes the request
6. If invalid, the server returns a 401 Unauthorized response

## Step 6: Best practices for production use

For production environments, consider these additional steps:

1. **Store user credentials securely**: Implement proper password hashing (BCrypt) and user database
2. **Secure the JWT secret**: Use environment variables or a secure key management service
3. **Add more claims validation**: Implement issuer, audience, and custom claims validation
4. **Enable CSRF protection** for web applications with cookies/sessions
5. **Configure CORS** properly if your APIs are called from different domains
6. **Add rate limiting** to prevent brute force attacks
7. **Implement token refresh** mechanism for longer sessions
8. **Use HTTPS** in all environments
9. **Add proper logging** for security events

## Troubleshooting

### Common issues:

1. **"Invalid token" errors**: Check token expiration and signature algorithm
2. **401 Unauthorized**: Verify that the token is correctly formatted in the Authorization header
3. **403 Forbidden**: Check that the user has the required roles/authorities
4. **Configuration issues**: Ensure your security configuration permits the correct endpoints

## Conclusion

You now have a working JWT-based authentication server with Spring Boot. This server can be extended to support more complex authentication scenarios, including:

- Role-based access control
- OAuth 2.0 with authorization codes
- Multi-factor authentication
- Token revocation
