
# Exercise
Implement [StringIsEmpty.java](https://github.com/moderneinc/rewrite-recipe-starter/blob/main/src/main/java/com/yourorg/StringIsEmpty.java)

## Implementation Details

The `StringIsEmpty` recipe uses Google's Refaster framework to replace verbose string length checks with the more idiomatic `isEmpty()` method.

### What was implemented:

The recipe defines two **before** patterns that should be replaced:
1. **Standard form**: `s.length() == 0`
2. **Reversed form**: `0 == s.length()` (Yoda condition)

And one **after** pattern:
- `s.isEmpty()`

### How it works:

```java
@BeforeTemplate
boolean lengthEqualsZero(String s) {
    return s.length() == 0;
}

@BeforeTemplate
boolean lengthEqualsZeroReversed(String s) {
    return 0 == s.length();
}

@AfterTemplate
boolean isEmpty(String s) {
    return s.isEmpty();
}
```

When the recipe runs, OpenRewrite will:
1. Scan your codebase for any occurrence of the before patterns
2. Replace them with the after pattern
3. Generate a patch file showing the changes

### Run the recipe

```bash
mvn clean rewrite:run -Drewrite.activeRecipes=com.yourorg.StringIsEmptyRecipe
```
Look for @StringIsEmpty in `recipes` folder for a sample code.
