No, if you're setting the authentication manually like this:

```java
String username = jwtTokenProvider.getUsername(token);
var auth = new UsernamePasswordAuthenticationToken(username, null, Collections.emptyList());
SecurityContextHolder.getContext().setAuthentication(auth);
```

Then **`authentication.getPrincipal()` will be a `String`** (i.e., the username), **not a `Jwt` object**, because you are manually creating a `UsernamePasswordAuthenticationToken` and passing the username as the principal.

So this would **not work**:

```java
Jwt jwt = (Jwt) authentication.getPrincipal(); // ❌ ClassCastException
```

Instead, you'd access it like this:

```java
String username = (String) authentication.getPrincipal(); // ✅ OK
```

---

### If You Want `authentication.getPrincipal()` to Be a `Jwt`

Then, in your JWT filter, you should use a different approach, like:

```java
Jwt jwt = jwtDecoder.decode(token);
Authentication auth = new JwtAuthenticationToken(jwt);
SecurityContextHolder.getContext().setAuthentication(auth);
```

Now, when your controller gets the `Authentication`, `authentication.getPrincipal()` **is a `Jwt` object**, and you can access all claims:

```java
Jwt jwt = (Jwt) authentication.getPrincipal();
String username = jwt.getSubject();
String email = jwt.getClaimAsString("email");
```

---

### Summary:

| Authentication Implementation                        | `getPrincipal()` Type | How to Access Username                               |
| ---------------------------------------------------- | --------------------- | ---------------------------------------------------- |
| `UsernamePasswordAuthenticationToken(username, ...)` | `String`              | `authentication.getPrincipal()` returns username     |
| `JwtAuthenticationToken(jwt)`                        | `Jwt`                 | `((Jwt) authentication.getPrincipal()).getSubject()` |

---
| Feature                             | `UsernamePasswordAuthenticationToken` | `JwtAuthenticationToken`  |
| ----------------------------------- | ------------------------------------- | ------------------------- |
| Stores full JWT and claims          | ❌ No                                  | ✅ Yes                     |
| Lets you fetch claims in controller | ❌ Needs extra parsing or services     | ✅ Directly via principal  |
| Cleaner Spring Security integration | ✅ Simple for basic cases              | ✅ Ideal for JWT scenarios |
| Better for microservices            | ❌ Limited context                     | ✅ Self-contained identity |

