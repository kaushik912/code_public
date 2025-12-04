# 🧠 JavaScript — How It Works Under the Hood

---

## 🧩 Setup

To experiment with JavaScript:

* Use **Chrome / IE Developer Tools**
* Use **Brackets.io** →
  `File → Open Folder` (contains your code)
  `View → Themes` (to change the editor theme)

---

## ⚙️ Conceptual Foundations

### Syntax Parser

A **syntax parser** is a program that reads your code, checks its grammar, and determines what it does.

### Execution Context

A **wrapper** that helps manage the code that’s currently running.
It contains more than just the code you write — it manages variables, functions, and the environment they execute in.

### Lexical Environment

Where something sits **physically** in the code.
“Lexical” refers to structure based on **words and grammar** — *where* you write something matters.

Example:

```js
function hello() {
  var a = 'Hello World';
}
```

Here, `a` exists *lexically* inside the `hello()` function.

Your code → parsed → compiled → computer instructions.
Functions and variables are handled based on *where they sit lexically.*

---

## 🌍 The Global Environment and the Global Object

The **base execution context** is the **Global Execution Context**, which automatically creates:

1. **Global Object**
2. **`this`** — a special variable referencing the current context

### Example Setup

```html
<html>
  <head></head>
  <body>
    <script src="app.js"></script>
  </body>
</html>
```

If `app.js` is empty and you run it, the JavaScript engine still:

* Creates an **execution context**
* Sets up the **Global Object**
* Defines **`this`**

In browsers:

* `this` === `window`
* `window` is the **global object**

In Node.js:

* The global object exists but isn’t `window`.

Each browser tab (window) has its **own execution context**.

### Example

```js
var a = 'Hello World!';
function b() {}
```

In Chrome console:

```js
window
```

Outputs something like:

```js
a: "Hello World!"
b: ƒ b() { ... }
```

So, variables and functions declared *outside any function* become properties of the **global object**.

```js
a;        // "Hello World!"
window.a; // "Hello World!"
```

---

## 🚀 The Execution Context: Creation and Hoisting

### Example

```js
var a = 'Hello World!';
function b() {
  console.log('Called b!');
}

b();
console.log(a);
```

**Output:**

```
Called b!
Hello World!
```

Now rearrange:

```js
b();
console.log(a);
var a = 'Hello World!';
function b() {
  console.log('Called b!');
}
```

**Output:**

```
Called b!
undefined
```

Even though the function was *below*, it worked — this is **hoisting**.

If we remove the variable declaration:

```js
b();
console.log(a);
function b() {
  console.log('Called b!');
}
```

We get:

```
Called b!
Uncaught ReferenceError: a is not defined
```

### 🧭 What is Hoisting?

Hoisting is when **JavaScript sets up memory space** for variables and functions before executing code.

* **Functions** are stored in memory *entirely.*
* **Variables** are initialized with the value `undefined`.

It only *appears* like things were “moved to the top.” In reality, the JS engine processes declarations first during the **creation phase** of the execution context.

Example:

```js
console.log(x); // undefined
var x = 5;
```

is internally treated like:

```js
var x;
console.log(x);
x = 5;
```

---

## 🧱 Execution Context Creation: The Two Phases

1. **Creation Phase**

   * Memory is allocated for functions and variables.
   * Variables are set to `undefined`.
   * Functions are stored entirely.

2. **Execution Phase**

   * Code is executed line by line.
   * Variable assignments are updated.

---

## ⚠️ Conceptual Aside — JavaScript and `undefined`

`undefined` is a special value meaning “a variable has been declared but not assigned.”

Example:

```js
var a;
console.log(a); // undefined

if (a === undefined) {
  console.log('a is undefined');
} else {
  console.log('a is defined');
}
```

**Important:**
Never manually set a variable to `undefined`.
You won’t be able to tell if *you* set it or if the JS engine did during creation.

---

## 🧵 Execution Context Model

JavaScript is:

* **Single-threaded:** executes one command at a time.
* **Synchronous:** executes in sequence, line by line.

Each piece of code runs in its own **execution context**, stacked one above another (the *execution stack*).

---

## 🧭 Functions, Context, and Variable Environment

* **Variable Environment:**
  Where variables live in memory and how they relate to each other within a given context.

Each function creates its own **execution context** and **variable environment** when invoked.

---

## 🔗 Scope Chain

When a variable is referenced, JavaScript looks for it in the **current scope** and then in its **outer environment**.

### Example 1

```js
function b() {
  console.log(myvar);
}

function a() {
  var myvar = 2;
  b();
}

var myvar = 1;
a(); // → 1
```

`b()` doesn’t find `myvar` in its own scope, so it checks its *outer environment* — which is the global scope.

### Example 2 — Lexical Scoping

```js
function a() {
  function b() {
    console.log(myvar);
  }
  var myvar = 2;
  b();
}

var myvar = 1;
a(); // → 2
```

Here, `b()` is **lexically inside** `a()`.
So when it doesn’t find `myvar` locally, it looks in `a()`’s scope, not the global one.

If you call `b();` outside `a();`, you’ll get a `ReferenceError` — `b` isn’t accessible globally.

### Example 3

```js
function a() {
  function b() {
    console.log(myvar);
  }
  b();
}

var myvar = 1;
a(); // → 1
```

`b()` → doesn’t find `myvar` locally → checks `a()` → still not found → goes to global scope → finds it.

---

## ⚡ Summary

| Concept                           | Description                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Execution Context**             | Environment where code is executed, consisting of variable object, scope chain, and `this`.         |
| **Global Execution Context**      | Default context; creates global object and `this`.                                                  |
| **Hoisting**                      | Declarations are processed before execution; functions fully hoisted, variables set to `undefined`. |
| **`undefined`**                   | Default uninitialized variable value; never manually assign.                                        |
| **Single-threaded & Synchronous** | One operation at a time, in order.                                                                  |
| **Lexical Scope & Scope Chain**   | Variable lookup proceeds outward through nested environments based on where functions are defined.  |

---