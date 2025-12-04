# Implementing JWT with Public/Private Key Authentication in Spring Boot
This guide explains how to implement JWT authentication using asymmetric keys (public/private key pairs) in a Spring Boot application. This approach provides enhanced security by keeping your private key secret while allowing token verification with the public key.

##  Create a skeleton project using Spring Initializr
curl https://start.spring.io/starter.zip \                                       
  -d dependencies=web,security,oauth2-authorization-server \
  -d type=maven-project \
  -d language=java \
  -d name=auth-server-crypto \
  -d packageName=com.example.auth \
  -d javaVersion=17 \
  -o auth-server-crypto.zip && unzip auth-server-crypto.zip -d auth-server-crypto

## Dependencies

First, add these dependencies to your pom.xml:

```xml
<!-- Spring Security -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- JWT -->
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
```

## Step 1: Generate RSA Key Pair

Generate a key pair using OpenSSL:

```bash
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

Place these files in resources.

## Step 2: Create a Key Utility Class

Create a utility class to load keys from PEM files:

```java
package com.example.auth.util;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.*;
import java.security.spec.*;
import java.util.Base64;

public class KeyUtil {

    public static PrivateKey getPrivateKey(String filename) throws Exception {
        String key = new String(Files.readAllBytes(Paths.get(filename)))
                .replaceAll("-----\\w+ PRIVATE KEY-----", "")
                .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(key);
        PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(decoded);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return kf.generatePrivate(keySpec);
    }

    public static PublicKey getPublicKey(String filename) throws Exception {
        String key = new String(Files.readAllBytes(Paths.get(filename)))
                .replaceAll("-----\\w+ PUBLIC KEY-----", "")
                .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(key);
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(decoded);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return kf.generatePublic(keySpec);
    }
}
```

## Step 3: Create JWT Token Provider

Create a service to handle JWT token generation and validation:

```java
package com.example.auth.util;

import io.jsonwebtoken.*;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.Date;

public class JwtTokenProvider {

    private final PrivateKey privateKey;
    private final PublicKey publicKey;
    private final long validityInMilliseconds = 3600000; // 1 hour

    public JwtTokenProvider(PrivateKey privateKey, PublicKey publicKey) {
        this.privateKey = privateKey;
        this.publicKey = publicKey;
    }

    public String createToken(String username) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + validityInMilliseconds);

        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(privateKey, SignatureAlgorithm.RS256)
                .compact();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(publicKey)
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    public String getUsername(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(publicKey)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }
}
```

## Step 4: Configure Spring Security

Create a security configuration class:

```java
package com.example.auth.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.filter.OncePerRequestFilter;

import com.example.auth.util.JwtTokenProvider;

import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Configuration
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;

    public SecurityConfig(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/token").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(new JwtTokenFilter(jwtTokenProvider), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    private static class JwtTokenFilter extends OncePerRequestFilter {

        private final JwtTokenProvider jwtTokenProvider;

        public JwtTokenFilter(JwtTokenProvider jwtTokenProvider) {
            this.jwtTokenProvider = jwtTokenProvider;
        }

        @Override
        protected void doFilterInternal(HttpServletRequest request,
                                        HttpServletResponse response,
                                        FilterChain filterChain) throws java.io.IOException, jakarta.servlet.ServletException {
            String authHeader = request.getHeader("Authorization");
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                String token = authHeader.substring(7);
                if (jwtTokenProvider.validateToken(token)) {
                    String username = jwtTokenProvider.getUsername(token);
                    var auth = new UsernamePasswordAuthenticationToken(username, null, java.util.Collections.emptyList());
                    SecurityContextHolder.getContext().setAuthentication(auth);
                }
            }
            filterChain.doFilter(request, response);
        }
    }
}
```

## Step 5: Create Authentication Model and Controller

Create a model for authentication requests:

```java
package com.example.auth.model;

public record AuthRequest(String username, String password) {}
```

Create a controller for authentication and protected endpoints:

```java
package com.example.auth.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.auth.model.AuthRequest;
import com.example.auth.util.JwtTokenProvider;
import org.springframework.security.core.Authentication;

@RestController
public class AuthController {

    private final JwtTokenProvider jwtTokenProvider;

    public AuthController(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @PostMapping("/token")
    public ResponseEntity<?> token(@RequestBody AuthRequest authRequest) {
        // In production, authenticate against a real user store
        if ("user".equals(authRequest.username()) && "password".equals(authRequest.password())) {
            String token = jwtTokenProvider.createToken(authRequest.username());
            return ResponseEntity.ok(new AuthResponse(token));
        }
        return ResponseEntity.status(401).body("Invalid username/password");
    }

    @GetMapping("/profile")
    public ResponseEntity<?> profile(Authentication authentication) {
        String username = (String) authentication.getPrincipal();
        return ResponseEntity.ok(new ProfileResponse(username, username+"@example.com", "+1234567890"));
    }

    static record AuthResponse(String token) {}
    static record ProfileResponse(String username, String email, String phone) {}
}
```

## Step 6: Configure the Application

Create the main application class with key initialization:

```java
package com.example.auth;

import java.security.PrivateKey;
import java.security.PublicKey;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.example.auth.util.JwtTokenProvider;
import com.example.auth.util.KeyUtil;

@SpringBootApplication
public class AuthServerCryptoApplication {

    public static void main(String[] args) {
        SpringApplication.run(AuthServerCryptoApplication.class, args);
    }

    @Bean
    public JwtTokenProvider jwtTokenProvider() throws Exception {
        PrivateKey privateKey = KeyUtil.getPrivateKey("src/main/resources/private_key.pem");
        PublicKey publicKey = KeyUtil.getPublicKey("src/main/resources/public_key.pem");
        return new JwtTokenProvider(privateKey, publicKey);
    }
}
```

## Testing with Postman

1. **Get a token**:
   - POST to `http://localhost:8080/token`
   - Body: `{"username": "user", "password": "password"}`
   - This will return a JWT token

2. **Access a protected resource**:
   - GET to `http://localhost:8080/profile`
   - Header: `Authorization: Bearer your_token_here`
   - You will receive the protected profile information

## How It Works

1. **Authentication Flow**:
   - User sends credentials to `/token`
   - Server validates credentials
   - Server generates JWT signed with private key
   - Client receives and stores the token

2. **Authorization Flow**:
   - Client includes token in Authorization header
   - `JwtTokenFilter` extracts and validates token using public key
   - If valid, the request proceeds to the controller
   - If invalid, access is denied with 401 response

3. **Security Benefits**:
   - Private key never leaves authentication server
   - Multiple services can verify tokens with just the public key
   - Tokens can include claims (user info) that are tamper-proof

This setup provides a secure, stateless authentication mechanism that works well in distributed systems and microservices architectures.