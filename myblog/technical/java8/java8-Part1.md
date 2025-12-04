# **Java 8 — Getting Started**

## **1. The Problem with Anonymous Classes**

Suppose we want to add an `ActionListener` to a button. Traditionally, we might write:

```java
button.addActionListener(
    new ActionListener() {
        public void actionPerformed(ActionEvent e) {
            System.out.println("Button Clicked");
        }
    }
);
```

While this works, it has some drawbacks:

* Too much **boilerplate code**.
* It **obscures the intent** of the programmer.
* We are giving the button an **object** that represents an action — think of it as *“code as data.”*

---

## **2. Enter Lambda Expressions**

With Java 8, the same logic can be expressed much more concisely:

```java
button.addActionListener(event -> System.out.println("Button Clicked"));
```

What’s happening here?

* It defines a **block of code** — a function without a name.
* `event` is the **parameter**.
* Instead of passing an object that implements an interface, we’re passing a **block of executable code**.
* We don’t specify the type of `event`; the compiler (**`javac`**) infers it as `ActionEvent`.

This concise syntax is called a **lambda expression**.

---

## **3. Different Forms of Lambda Expressions**

Lambdas in Java can take many forms depending on parameters and logic:

| Case                    | Example                                                                                        | Description                         |
| ----------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------- |
| **No arguments**        | `() -> System.out.println("Hello World!")`                                                     | Executes a statement without inputs |
| **Single argument**     | `event -> System.out.println("Button Clicked")`                                                | Takes one parameter                 |
| **Multiple statements** | <pre>() -> {<br>   System.out.println("Hello");<br>   System.out.println("World!");<br>}</pre> | Encloses multiple lines in braces   |

---

## **4. Functional Interfaces**

A **Functional Interface** is an interface with a **single abstract method (SAM)**.
Lambda expressions provide an implementation for that single method.

### Common Functional Interfaces in Java 8

| Interface           | Arguments | Returns | Method     | Example Use Case              |
| ------------------- | --------- | ------- | ---------- | ----------------------------- |
| `Predicate<T>`      | T         | boolean | `test()`   | Check if an album is released |
| `Consumer<T>`       | T         | void    | `accept()` | Print track titles            |
| `Supplier<T>`       | None      | T       | `get()`    | Factory method                |
| `UnaryOperator<T>`  | T         | T       | `apply()`  | Logical NOT, increment, etc.  |
| `BinaryOperator<T>` | T, T      | T       | `apply()`  | Multiply two numbers          |
| `Function<T,R>`     | T         | R       | `apply()`  | Extract name from an artist   |

Import all at once using:

```java
import java.util.function.*;
```

---

## **5. Exercises**

### **Exercise 1: Identify Functional Interface**

> **Question:** `ActionListener` takes an `ActionEvent` as input and returns `void`.
> Which functional interface does this correspond to?

**Answer:**
`Consumer<T>` — since it accepts an input (T) and returns nothing (`void`).

---

### **Exercise 2: Predicate Example**

> Define a predicate to check if a number is greater than 5.

A `Predicate<T>` is defined as:

```java
public interface Predicate<T> {
    boolean test(T t);
}
```

Implementation:

```java
Predicate<Integer> greaterThan5 = x -> x > 5;
```

Usage:

```java
System.out.println(greaterThan5.test(10)); // true
System.out.println(greaterThan5.test(2));  // false
```

---

### **Exercise 3: BinaryOperator Example**

> Write a `BinaryOperator` to multiply two `Long` values.

```java
BinaryOperator<Long> multiplyLongs = (x, y) -> x * y;
System.out.println(multiplyLongs.apply(10L, 20L)); // Prints 200
```

⚠️ Note:
You must specify the type explicitly — this will **not compile**:

```java
BinaryOperator multiplyLongs = (x, y) -> x * y; // Error: Type inference fails
```

---

### **Exercise 4: Function Interface**

The `Function<T,R>` interface looks like this:

```java
public interface Function<T,R> {
    R apply(T t);
}
```

It’s widely used in **Stream APIs**.

> Write a `Function` that computes the square root of an integer.

```java
Function<Integer, Double> sqrtFunction = x -> Math.sqrt(x);
System.out.println(sqrtFunction.apply(100)); // Prints 10.0
```

---

### **Exercise 5: Validate Function Implementations**

Which of these are valid `Function<Long, Long>` implementations?

```java
x -> x + 1
(x, y) -> x + 1
x -> x == 1
```

**Answer:**

| Expression        | Valid? | Reason                        |
| ----------------- | ------ | ----------------------------- |
| `x -> x + 1`      | ✅      | Takes one arg, returns a long |
| `(x, y) -> x + 1` | ❌      | Takes two args → BiFunction   |
| `x -> x == 1`     | ❌      | Returns boolean → Predicate   |

---

### **Exercise 6: Thread-Safe DateFormat**

> Implement a thread-safe `DateFormat` using `ThreadLocal`.

```java
ThreadLocal<DateFormatter> dfm =
    ThreadLocal.withInitial(() -> new DateFormatter());
```

Here, `withInitial()` accepts a **Supplier**, providing a new instance for each thread.

---

## **6. Type Inference**

Java 8 improves type inference in many contexts.

For example:

```java
Map<String, String> map = new HashMap<>();
```

The compiler automatically infers the type parameters on the right-hand side.

Similarly, in lambdas, parameter types can often be inferred:

```java
button.addActionListener(event -> System.out.println("Button Clicked"));
```

You can, however, **explicitly specify** them for clarity:

```java
button.addActionListener((ActionEvent event) -> System.out.println("Button Clicked"));
```

Explicit typing can **improve readability and reduce ambiguity** in complex expressions.

---

✅ **Summary**

* Lambdas make Java more expressive by eliminating anonymous class boilerplate.
* Functional Interfaces form the foundation of the **Java 8 functional programming model**.
* `Predicate`, `Consumer`, `Supplier`, and `Function` are key building blocks.
* Type inference simplifies syntax but explicit types can aid readability.

---

