# Complete Guide to JWT Authentication with RSA Public/Private Keys in Spring Boot

This comprehensive guide explains how to implement secure authentication in a Spring Boot application using JWT with RSA public/private key signing. This approach offers significant security advantages over symmetric key signing.

## Table of Contents

1. Introduction
2. Project Setup
3. Required Dependencies
4. Generate RSA Key Pair
5. Key Utility Class
6. JWT Token Provider
7. RSA Key Configuration
8. Security Configuration
9. Authentication Controller
10. Role-Based Authorization
11. Testing the Solution
12. How It Works

## Introduction

Using asymmetric keys for JWT authentication enhances security:
- **Private key**: Kept secret and used only by the authentication server to sign tokens
- **Public key**: Can be shared with any service that needs to verify token authenticity
- **Advantage**: Even if the public key is compromised, attackers cannot forge tokens

## Project Setup

First, create a Spring Boot project with required dependencies using Spring Initializr:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,security,oauth2-authorization-server \
  -d type=maven-project \
  -d language=java \
  -d name=auth-server-crypto \
  -d packageName=com.example.auth \
  -d javaVersion=17 \
  -o auth-server-crypto.zip && unzip auth-server-crypto.zip
```

## Required Dependencies

Add these dependencies to your pom.xml:

```xml
<!-- Spring Security and Web -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-authorization-server</artifactId>
</dependency>

<!-- JWT Libraries -->
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

## Generate RSA Key Pair

Generate RSA key pair using OpenSSL:

```bash
# Generate private key
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

# Extract public key from private key
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

Place these files in resources.

## Key Utility Class

This class loads RSA keys from PEM files:

```java
package com.example.auth.util;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyFactory;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

public class KeyUtil {

    public static RSAPrivateKey getPrivateKey(String filename) throws Exception {
        String key = new String(Files.readAllBytes(Paths.get(filename)))
                .replaceAll("-----\\w+ PRIVATE KEY-----", "")
                .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(key);
        PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(decoded);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return (RSAPrivateKey) kf.generatePrivate(keySpec);
    }

    public static RSAPublicKey getPublicKey(String filename) throws Exception {
        String key = new String(Files.readAllBytes(Paths.get(filename)))
                .replaceAll("-----\\w+ PUBLIC KEY-----", "")
                .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(key);
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(decoded);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return (RSAPublicKey) kf.generatePublic(keySpec);
    }
}
```

## JWT Token Provider

Class that handles JWT token generation with RSA signing:

```java
package com.example.auth.util;
import io.jsonwebtoken.*;
import java.security.PrivateKey;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JwtTokenProvider {

    private final PrivateKey privateKey;
    private final long validityInMilliseconds = 5 * 60 * 1000; // 5 mins

    public JwtTokenProvider(PrivateKey privateKey) {
        this.privateKey = privateKey;
    }

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
}
```

## RSA Key Configuration

Configuration bean to make keys available for dependency injection:

```java
package com.example.auth.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.example.auth.util.KeyUtil;

import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;

@Configuration
public class RsaKeyConfig {

    @Bean
    public RSAPrivateKey privateKey() throws Exception {
        return KeyUtil.getPrivateKey("src/main/resources/private_key.pem");
    }

    @Bean
    public RSAPublicKey publicKey() throws Exception {
        return KeyUtil.getPublicKey("src/main/resources/public_key.pem");
    }
}
```

## Application Main Class

Register the JWT token provider:

```java
package com.example.auth;

import java.security.PrivateKey;
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
        return new JwtTokenProvider(privateKey);
    }
}
```

## Security Configuration

Configure Spring Security to use JWT for authentication with role support:

```java
package com.example.auth.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;

import java.security.interfaces.RSAPublicKey;
import java.util.List;
import java.util.stream.Collectors;

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
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/token").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.decoder(jwtDecoder())
                .jwtAuthenticationConverter(jwtAuthenticationConverter()))
            );

        return http.build();
    }
}
```

## Authentication Model

Create a simple model for authentication requests:

```java
package com.example.auth.model;

public record AuthRequest(String username, String password) {}
```

## Authentication Controller

Create a controller for token generation and accessing protected endpoints:

```java
package com.example.auth.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.auth.model.AuthRequest;
import com.example.auth.util.JwtTokenProvider;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.jwt.Jwt;

@RestController
public class AuthController {

    private final JwtTokenProvider jwtTokenProvider;

    public AuthController(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    // Simple username/password check for demo
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

    @GetMapping("/profile")
    public ResponseEntity<?> profile(Authentication authentication) {
        Jwt jwt = (Jwt) authentication.getPrincipal();
        String username = jwt.getSubject();
        return ResponseEntity.ok(new ProfileResponse(username, username+"@example.com", "+1234567890"));
    }

    static record AuthResponse(String token) {}
    static record ProfileResponse(String username, String email, String phone) {}
}
```

## Role-Based Authorization

Create a controller with role-based access controls:

```java
package com.example.auth.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RoleController {

    @GetMapping("/api/user")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<String> userEndpoint() {
        return ResponseEntity.ok("Hello, USER!");
    }

    @GetMapping("/api/admin")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> adminEndpoint() {
        return ResponseEntity.ok("Hello, ADMIN!");
    }

    @GetMapping("/api/dev")
    @PreAuthorize("hasRole('DEV')")
    public ResponseEntity<String> devEndpoint() {
        return ResponseEntity.ok("Hello, DEVELOPER!");
    }
}
```

## Testing the Solution

### 1. Using Postman

#### Get a token:
- **Method**: POST
- **URL**: `http://localhost:8080/token`
- **Body**: `{"username": "admin"}`
- **Response**: JWT token

#### Access protected resources:
- **Method**: GET
- **URL**: `http://localhost:8080/profile`
- **Headers**: `Authorization: Bearer <your_token>`

#### Test role-based endpoints:
- **URL**: `http://localhost:8080/api/admin` (requires ADMIN role)
- **URL**: `http://localhost:8080/api/user` (requires USER role)
- **URL**: `http://localhost:8080/api/dev` (requires DEV role)

### 2. Using cURL

```bash
# Get token
curl -X POST http://localhost:8080/token -H "Content-Type: application/json" -d '{"username": "admin"}'

# Use token to access profile
curl -X GET http://localhost:8080/profile -H "Authorization: Bearer <your_token>"

# Access admin endpoint
curl -X GET http://localhost:8080/api/admin -H "Authorization: Bearer <your_token>"
```

## How It Works

### Token Generation Flow

1. Client submits username to `/token` endpoint
2. Server generates JWT token:
   - Sets the subject claim to username
   - Adds roles as custom claims
   - Sets expiration time (5 minutes)
   - Signs the token using RSA private key
3. Server returns the signed JWT token

### Authentication Flow

1. Client includes JWT in Authorization header: `Bearer <token>`
2. Spring Security:
   - Extracts the token from the header
   - Uses `JwtDecoder` to validate token with public key
   - Validates token expiration
   - Creates a `JwtAuthenticationToken` with extracted claims
   - Converts roles claim to Spring Security authorities
   - Sets authentication in `SecurityContext`
3. Request proceeds to controller if authentication succeeds

### JWT Structure

A JWT consists of three parts:
1. **Header**: Algorithm and token type
   ```json
   {
     "alg": "RS256",
     "typ": "JWT"
   }
   ```

2. **Payload**: User claims
   ```json
   {
     "sub": "admin",
     "roles": ["ADMIN", "USER"],
     "iat": 1674926371,
     "exp": 1674926671
   }
   ```

3. **Signature**: Created with private key
   ```
   RSASHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     privateKey
   )
   ```

## Security Benefits

1. **Secure Signature**: Public key cryptography ensures only tokens signed by your private key are accepted
2. **Stateless Authentication**: No session storage required on server
3. **Secure Key Management**: Private key never leaves authentication server
4. **Distributed Verification**: Multiple services can validate tokens with just the public key
5. **Role-based Authorization**: User roles included in token claims enable fine-grained access control

By following this guide, you would have implemented a robust authentication system that leverages the security benefits of RSA public/private key cryptography for JWT authentication in Spring Boot.

