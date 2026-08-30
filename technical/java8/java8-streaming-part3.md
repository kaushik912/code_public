
## Common Stream Operations in Java

In this post, we’ll explore some frequently used **Stream operations** in Java, comparing traditional Java 7 approaches with modern Java 8 Stream API equivalents.

---

### 1. Collecting Elements into a List

**Operation:** `collect(Collectors.toList())`

This is an **eager terminal operation**, which means it triggers the evaluation of the Stream and collects the resulting elements into a list.

**Example:**

```java
List<String> collected = Stream.of("a", "b", "c")
                               .collect(Collectors.toList());

assertEquals(Arrays.asList("a", "b", "c"), collected);
```

✅ Here, we convert the Stream of strings into a `List<String>`.

---

### 2. Converting Strings to Uppercase

#### Java 7 Approach

```java
List<String> collected = new ArrayList<>();
for (String string : Arrays.asList("a", "b", "hello")) {
    String upperCase = string.toUpperCase();
    collected.add(upperCase);
}
```

#### Java 8 Stream Approach

```java
List<String> collected = Stream.of("a", "b", "hello")
                               .map(string -> string.toUpperCase())
                               .collect(Collectors.toList());
```

✅ The `map()` operation applies a transformation to each element of the Stream.
In this case, we convert each string to uppercase before collecting the results into a list.

---

### 3. Filtering Strings That Start with a Number

#### Java 7 Approach

```java
List<String> beginningWithNumber = new ArrayList<>();
for (String string : Arrays.asList("a", "b", "hello")) {
    if (Character.isDigit(string.charAt(0))) {
        beginningWithNumber.add(string);
    }
}
```

#### Java 8 Stream Approach

```java
List<String> beginningWithNumber = Stream.of("a", "b", "hello")
                                         .filter(string -> Character.isDigit(string.charAt(0)))
                                         .collect(Collectors.toList());
```

✅ The `filter()` operation retains only elements that satisfy a given condition.
Here, the condition is defined by a **Predicate**, a functional interface that returns a boolean.

---

### Key Takeaways

* **`map()`** transforms elements in a stream.
* **`filter()`** selects elements based on a condition.
* **`collect()`** gathers the processed results into a collection (like a `List`).
* Streams enable **concise**, **readable**, and **functional** data transformations compared to imperative loops.

