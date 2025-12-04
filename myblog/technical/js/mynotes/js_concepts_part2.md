# 🧭 JavaScript Ready-Reckoner

## 1. Scope, ES6, and `let`

### Scope

**Scope** determines where a variable is accessible in your code. Variables can be globally, functionally, or block-scoped.

### ES6 Variable Declarations

ES6 introduced new keywords for variable declaration:

* `let` — block-scoped (available only inside the block it’s declared in)
* `const` — block-scoped and immutable (cannot be reassigned)
* `var` — function-scoped (older syntax; still valid)

Example:

```js
if (a > b) {
  let c = true;
  console.log(c); // Accessible here
}
console.log(c); // ReferenceError – c is not defined outside the block
```

A **block** is defined by curly braces `{}` (e.g., inside `if`, `for`, `while`).

---

## 2. Asynchronous Callbacks

### What is Asynchronous?

Asynchronous means more than one thing happening at a time.
Although JavaScript executes code **synchronously** (line by line), the **browser** handles asynchronous events (like clicks, HTTP requests) in the **event queue**.

### Event Queue and Event Loop

* Events (clicks, requests) are placed in the **event queue**.
* The **execution stack** must be empty before queued events are processed.
* The **event loop** continuously checks whether the stack is empty to process new events.

Example:

```js
function waitThreeSeconds() {
  var ms = 3000 + new Date().getTime();
  while (new Date() < ms) {}
  console.log('Finished Function');
}

function clickHandler() {
  console.log('click event');
}

document.addEventListener('click', clickHandler);
waitThreeSeconds();
console.log('finished execution');
```

**Log Output (after 3 seconds):**

```
Finished Function
finished execution
click event
```

JS won’t check the event queue until the execution stack is empty — meaning long-running tasks block other events.

---

## 3. JavaScript and Types

### Dynamic Typing

In JavaScript, you don’t declare variable types explicitly — the engine determines the type **at runtime**.

```js
var isNew = true;
isNew = 'yup';
isNew = 1;
```

### Static Typing (for contrast)

In statically-typed languages:

```c
bool isNew = 'hello'; // Error
```

---

## 4. Primitive Types

Primitives represent single values (not objects).
JavaScript has **6 primitive types**:

1. **undefined** – lack of assigned value (engine-assigned)
2. **null** – intentional lack of value (developer-assigned)
3. **boolean** – `true` or `false`
4. **number** – all numeric values (floating point by default)
5. **string** – sequence of characters (`' '` or `" "`)
6. **symbol** – unique identifiers (introduced in ES6; not fully supported in older browsers)

---

## 5. Operators and Coercion

### Operators

Operators are functions written with special syntax.
Example:

```js
var a = 3 + 4; // '+' is an operator
```

### Operator Precedence and Associativity

* **Precedence**: which operator executes first
* **Associativity**: execution order for operators with equal precedence (left→right or right→left)

Example:

```js
var a = 3 + 4 + 5; // evaluated left to right
```

See MDN for the full precedence table.

---

### Type Coercion

**Coercion** is automatic type conversion (e.g., number → string).

```js
var a = 1 + '2';
console.log(a); // "12" (1 coerced to "1")
```

---

## 6. Comparison Operators

### Chained Comparisons

```js
console.log(1 < 2 < 3); // true
console.log(3 < 2 < 1); // true (!)
```

Explanation:

* `<` has left-to-right associativity.
* `3 < 2` → `false`, then `false < 1` → `0 < 1` → `true`.

You can inspect coercion using `Number(value)`:

```js
Number(false); // 0
Number(true);  // 1
Number(undefined); // NaN
Number(null); // 0
```

---

## 7. Equality and Strict Equality

### Loose Equality `==`

Allows coercion:

```js
3 == "3"       // true
false == 0     // true
"" == 0        // true
" " == false   // true
null == 0      // false
```

### Strict Equality `===`

No coercion — compares both **value** and **type**:

```js
3 === 3        // true
"3" === 3      // false
false === 0    // false
```

**Recommendation:**
Use `===` and `!==` by default; avoid `==` and `!=` unless intentional coercion is required.

Example:

```js
var a = 0;
var b = false;

if (a === b) {
  console.log("equal");
} else {
  console.log("not equal");
}
// Output: not equal
```

---

## 8. Boolean Conversion

Values that coerce to `false` (falsy):

* `undefined`
* `null`
* `""`
* `0`
* `NaN`
* `false`

Everything else is truthy.

Example:

```js
var a;
if (a) {
  console.log("something there");
} // won't print anything
```

To handle `0` as a valid value:

```js
if (a || a === 0) {
  console.log("something there");
}
```

(`===` has higher precedence than `||`)

---

## 9. Default Values

### Missing Arguments

```js
function greet(name) {
  console.log("Hello " + name);
}

greet("Tony"); // Hello Tony
greet();       // Hello undefined
```

### Default Value Trick

Using logical OR (`||`):

```js
function greet(name) {
  name = name || "your_name_here";
  console.log("Hello " + name);
}

greet(); // Hello your_name_here
```

### OR (`||`) Behavior

Returns the first truthy value:

```js
true || false;     // true
undefined || "Hi"; // "Hi"
0 || 1;            // 1
"" || "Hello";     // "Hello"
```

---

## 10. Framework Aside — Global Collisions

Consider:

```html
<script src="lib1.js"></script>
<script src="lib2.js"></script>
<script src="app.js"></script>
```

`lib1.js`

```js
var libraryName = "Lib 1";
```

`lib2.js`

```js
var libraryName = "Lib 2";
```

`app.js`

```js
console.log(libraryName); // Lib 2
```

The second declaration overwrites the first (global namespace collision).

### Fix Using Global Checks

```js
window.libraryName = window.libraryName || "Lib 2";
```

Now, `libraryName` retains its first defined value (`Lib 1`).

Frameworks often use this pattern to prevent overwriting global variables.

---

# ✅ Key Takeaways

* Prefer `let` and `const` over `var`.
* Understand event loop behavior — JS is single-threaded but handles async tasks via queues.
* Be cautious with coercion and equality — use `===` and `!==`.
* Use `||` for default values, but beware of falsy values like `0`.
* Manage global scope carefully to avoid collisions in multi-script environments.

---

Would you like me to export this guide into a **PDF** or **Markdown** file for easy reference or sharing?
