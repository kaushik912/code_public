This guide explains how to implement JWT authentication in a Spring Boot application using asymmetric cryptography (public/private key pairs) for enhanced security.

## Table of Contents

1. Introduction
2. Project Setup
3. Key Generation
4. Dependencies
5. Key Configuration
6. JWT Token Provider
7. Security Configuration
8. Authentication Controller
9. Testing with Postman
10. How It Works

## Introduction

Using asymmetric keys (public/private key pairs) for JWT authentication offers significant security advantages over symmetric keys:

- **Private key**: Used only by the authentication server to sign tokens
- **Public key**: Distributed to any service that needs to verify tokens
- **Security benefit**: Your signing key (private) remains secret even when verification key (public) is shared

## Project Setup

Create a Spring Boot project with security dependencies. You can use Spring Initializr:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,security,oauth2-authorization-server \
  -d type=maven-project \
  -d language=java \
  -d name=auth-server-crypto \
  -d packageName=com.example.auth \
  -d javaVersion=17 \
  -o auth-server-crypto.zip && unzip auth-server-crypto.zip -d auth-server-crypto
```

## Key Generation

Generate RSA key pair using OpenSSL:

```bash
# Generate private key
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

# Extract public key from private key
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

Place these files in resources.

## Dependencies

Add these dependencies to your pom.xml:

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
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-authorization-server</artifactId>
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

## Key Configuration

1. First, create a utility class to load RSA keys from PEM files:

```java
// filepath: src/main/java/com/example/auth/util/KeyUtil.java
package com.example.auth.util;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.*;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.*;
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

2. Create a configuration class to expose the keys as Spring beans:

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

## JWT Token Provider

Create a service to handle JWT token generation (signing):

```java
package com.example.auth.util;
import io.jsonwebtoken.*;
import java.security.PrivateKey;
import java.util.Date;

public class JwtTokenProvider {

    private final PrivateKey privateKey;
    private final long validityInMilliseconds = 5 * 60 * 1000; // 5 mins

    public JwtTokenProvider(PrivateKey privateKey) {
        this.privateKey = privateKey;
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
}
```

Register the JWT token provider in the main application class:

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

Configure Spring Security to use JWT for authentication:

```java
package com.example.auth.config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;

import java.security.interfaces.RSAPublicKey;

@Configuration
public class SecurityConfig {

    private final RSAPublicKey publicKey; 

    public SecurityConfig(RSAPublicKey publicKey) {
        this.publicKey = publicKey;
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withPublicKey(publicKey).build();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, JwtDecoder jwtDecoder) throws Exception {
        http
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/token").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt());

        return http.build();
    }
}
```

## Authentication Model and Controller

1. Create a simple authentication request model:

```java
package com.example.auth.model;

public record AuthRequest(String username, String password) {}
```

2. Create a controller for authentication and protected endpoints:

```java
package com.example.auth.controller;

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
        if ("user".equals(authRequest.username()) && "password".equals(authRequest.password())) {
            String token = jwtTokenProvider.createToken(authRequest.username());
            return ResponseEntity.ok(new AuthResponse(token));
        }
        return ResponseEntity.status(401).body("Invalid username/password");
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

## Testing with Postman

1. **Get a token**:
   - **Method**: POST
   - **URL**: `http://localhost:8080/token`
   - **Headers**: `Content-Type: application/json`
   - **Body**: `{"username": "user", "password": "password"}`
   - This will return a JWT token

2. **Access protected profile**:
   - **Method**: GET
   - **URL**: `http://localhost:8080/profile`
   - **Headers**: `Authorization: Bearer <your_token_here>`
   - This will return user profile information if token is valid

## How It Works

### Authentication Flow:

1. **Token Generation**:
   - User provides credentials to `/token` endpoint
   - Server validates credentials
   - Server generates a JWT signed with the private RSA key
   - Token is returned to the client

2. **Request Authentication**:
   - Client includes JWT in `Authorization: Bearer <token>` header
   - Spring Security extracts the JWT from the request
   - `JwtDecoder` validates the token signature using the public RSA key
   - If valid, Spring creates a `JwtAuthenticationToken` with the JWT as principal
   - Request proceeds to controller if authentication succeeds
   - Controller can access JWT claims via the Authentication object

### Security Benefits:

1. **Signature Verification**: Public key cryptography ensures only tokens signed by your private key are accepted
2. **Stateless Authentication**: No session storage needed on the server
3. **Secure Key Management**: Private key never leaves authentication server
4. **Distributed Verification**: Multiple microservices can validate tokens with just the public key
5. **Self-contained**: Token includes all necessary user information (claims)

### Token Structure:

A JWT consists of three parts separated by periods:
1. **Header**: Algorithm and token type
2. **Payload**: Claims (user data, expiration time)
3. **Signature**: Created using the private key to verify authenticity

The signature ensures that:
- The token was created by a trusted source (who has the private key)
- The token hasn't been tampered with since it was signed

## Summary

By using asymmetric keys for JWT authentication, you've created a more secure authentication system than with traditional shared secrets. The private key is only used for signing tokens, while the public key can be safely distributed to any service that needs to verify those tokens.

This pattern is especially powerful in microservice architectures, where a dedicated authentication service can issue tokens that are verifiable by any other service without requiring them to share sensitive secrets.