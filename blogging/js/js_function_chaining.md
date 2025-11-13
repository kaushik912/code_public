🌟 **Function chaining through multiple closures (a) => (b) => (c) => ...**

Let’s explore this properly so it *clicks*.

---

## 🧩 The General Pattern

Yes — you can chain **any number** of arrow functions like this:

```js
(a) => (b) => (c) => expression
```

That means:

> “A function that takes `a` and returns another function that takes `b`,
> which returns another function that takes `c`,
> which finally returns the result (`expression`).”

It’s basically a chain of functions, each capturing the previous arguments via **closures**.

---

## 🧠 Expand to Understand

Let’s expand it into the normal `function` syntax to see what’s happening:

```js
function outer(a) {
  return function middle(b) {
    return function inner(c) {
      return a + b + c; // or any logic using all three
    };
  };
}
```

Now the arrow equivalent:

```js
const outer = (a) => (b) => (c) => a + b + c;
```

Both do the same thing.
Each inner function **closes over** its outer variables (`a`, `b`).

---

## 🚀 Example 1: Triple-Argument Adder

```js
const add3 = (a) => (b) => (c) => a + b + c;

console.log(add3(1)(2)(3)); // 6
```

**Step-by-step:**

1. Call `add3(1)` → returns `(b) => (c) => 1 + b + c`
2. Then call that with `2` → returns `(c) => 1 + 2 + c`
3. Finally call that with `3` → returns `6`

🧠 Each step keeps remembering the previous arguments!

---

## ⚙️ Example 2: Sentence Builder (String Closures)

```js
const sentence = (subject) => (verb) => (object) =>
  `${subject} ${verb} ${object}.`;

console.log(sentence("Kaushik")("loves")("JavaScript"));
// Output: "Kaushik loves JavaScript."
```

Each function adds one part of the sentence — and together they build the final string.
This is closure and currying *in a nutshell*.

---

## 💡 Example 3: Configurable Logger

```js
const logger = (prefix) => (level) => (message) =>
  console.log(`[${prefix} - ${level.toUpperCase()}] ${message}`);

const appLogger = logger("App");
const errorLogger = appLogger("error");
const infoLogger = appLogger("info");

errorLogger("Something went wrong!");
infoLogger("App started successfully.");
```

Output:

```
[App - ERROR] Something went wrong!
[App - INFO] App started successfully.
```

Here, we’re using **three layers of closures** to create specialized loggers:

* 1st level remembers the app name.
* 2nd level remembers the log level.
* 3rd level prints messages.

---

## 🧩 So How Many Layers Can You Have?

As many as you want!
Each arrow `(x) =>` adds one new layer — one more closure that can “remember” data from its outer scope.

For example:

```js
(a) => (b) => (c) => (d) => (e) => a + b + c + d + e
```

is perfectly valid JavaScript.

But usually, more than 3 levels gets hard to read — at that point, it’s better to “uncurry” or refactor.

---

## 🧠 Why Use These Patterns?

| Concept               | Benefit                                                                             |
| --------------------- | ----------------------------------------------------------------------------------- |
| **Currying**          | Transform a function taking multiple args into nested single-arg functions.         |
| **Closures**          | Each nested function keeps access to the arguments of outer functions.              |
| **Function Reuse**    | You can “partially apply” some arguments and reuse the returned function later.     |
| **Declarative Style** | Makes your code more expressive and modular (especially in functional programming). |

---

## 🔍 Example — Partial Application Demo

```js
const multiply = (a) => (b) => a * b;

const double = multiply(2); // partially applied
console.log(double(5)); // 10
```

Same concept — just more layers when needed.

---

### 🧠 TL;DR

Yes — you can have **any number** of chained arrow functions like `(a)=>(b)=>(c)`.
Each layer adds a **closure**, remembering the previous variable(s).
It’s the foundation of **currying**, **function factories**, and **partial application**.

