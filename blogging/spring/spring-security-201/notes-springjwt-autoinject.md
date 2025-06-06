To return the **username (or name)** extracted from the JWT token when the user calls the `/profile` endpoint in your **asymmetric JWT (public/private key) setup**, follow the steps below.

---

### ✅ Step 1: Extract Username from the Token

Spring Security automatically parses the JWT and builds a `Jwt` object. You can access it by injecting either:

* `@AuthenticationPrincipal Jwt jwt`
* Or: `Authentication authentication` and cast `authentication.getPrincipal()`

Let’s go with the **cleaner** `@AuthenticationPrincipal Jwt` approach.

---

### ✅ Step 2: Modify the `/profile` Controller

```java
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class UserController {

    @GetMapping("/profile")
    public Map<String, String> getProfile(@AuthenticationPrincipal Jwt jwt) {
        String username = jwt.getSubject(); // typically 'sub' claim
        // Or if you added a custom claim like 'name':
        // String name = jwt.getClaim("name");

        return Map.of(
            "message", "Welcome to your profile!",
            "username", username
        );
    }
}
```

---

### 🔍 Example Response

If your JWT contains:

```json
{
  "sub": "john",
  "name": "John Doe",
  "iat": 1717628851,
  "exp": 1717629151
}
```

The `/profile` endpoint would return:

```json
{
  "message": "Welcome to your profile!",
  "username": "john"
}
```

---

### ✅ Notes

* `jwt.getSubject()` maps to the `sub` claim in the token.
* You can extract **any custom claim** using `jwt.getClaim("claimName")`.
* No need to decode the token manually — Spring Security takes care of it.
