# 🧠 JavaScript Ready-Reckoner — Notes by Kaushik

---

## 🧩 Arrays

```js
var arr = new Array();
```

Instead, prefer:

```js
var arr = [];
var arr = [1, 2, 3];
```

Access elements using `arr[0]`, `arr[1]`, etc.
JavaScript arrays can hold **different kinds of values** — numbers, booleans, objects, functions, or even other arrays.

Example:

```js
var arr = [
  1,
  false,
  { name: 'Kaushik', address: 'BG road' },
  function(name) { var greeting = 'Hello '; console.log(greeting + name); },
  "hello"
];

console.log(arr); // No error → [1, false, {...}, f, "hello"]
arr[3]("Kaushik"); // Hello Kaushik
arr[3](arr[2].name); // Hello Kaushik
```

---

## 🧮 Arguments and Spread

### The `arguments` keyword

The special `arguments` object contains **all parameters passed to a function**, whether defined or not.

```js
function greet(firstName, lastName, language) {
  language = language || "en";
  console.log(firstName);
  console.log(lastName);
  console.log(language);
  console.log(arguments); // auto-available by JS
}
```

You can check for missing parameters:

```js
if (arguments.length === 0) {
  console.log('Missing parameters!');
  return;
}
```

### Spread syntax

```js
function greet(firstName, lastName, language, ...other) {
  // 'other' collects extra arguments into an array
}

greet('Kaushik', 'BK', 'es', 'BG road', 'BNG');
```

📘 **Conceptual Aside:**
The `arguments` object is **array-like**, not an array. Use spread (`...args`) for true arrays and modern iteration.

---

## 🧩 Conceptual Aside: Syntax Parsers

A **syntax parser** makes subtle changes to your code before it’s executed.
That’s why certain “automatic” behaviors in JavaScript exist.

---

## ⚠️ Dangerous Aside: Automatic Semicolon Insertion

You should **always** put your own semicolons!

Example:

```js
function getPerson() {
  return  // ← carriage return here!
  { firstName: 'Kaushik' }
}

console.log(getPerson()); // prints undefined
```

Why?
Because JS automatically inserts a semicolon after `return`:

```js
function getPerson() {
  return; // inserted automatically!
  { firstName: 'Kaushik' }
}
```

✅ **Fix:**

```js
function getPerson() {
  return {
    firstName: 'Kaushik'
  }
}
```

---

## ✍️ Framework Aside: Whitespace

JavaScript allows **liberal use of whitespace** — indentation and line breaks won’t affect execution.
Still, maintain consistent formatting for readability.

---

## ⚡ IIFE — Immediately Invoked Function Expressions

### Example 1: Simple IIFE

```js
var greeting = function(name) {
  console.log('Hello ' + name);
}(); // IIFE
```

### Example 2: Returning a Value

```js
var greeting = function(name) {
  return 'Hello ' + name;
}();  
console.log(greeting); // Hello undefined
```

Fix:

```js
var greeting = function(name) {
  return 'Hello ' + name;
}('Kaushik');  
console.log(greeting); // Hello Kaushik
```

### Function Expressions vs. Statements

```js
function(name) {
  return 'hello' + name;
} // ❌ Error: expects a name (function statement)
```

Wrap in parentheses to make it an **expression**:

```js
(function(name) {
  return 'hello' + name;
});
```

Inside parentheses, JS expects **expressions**, not statements.
So we **trick the syntax parser** into treating it correctly.

### Full IIFE Invocation:

```js
(function(name) {
  return 'hello ' + name;
}('Kaushik'));
```

Alternate style (both equivalent):

```js
(function(name) {
  return 'hello ' + name;
})(firstName);
```

📘 **Conceptual Aside:**
Be consistent with your preferred style — both are valid.

---

## 🧱 Framework Aside: IIFE and Safe Code

Many JavaScript **frameworks** use IIFEs to **avoid variable collisions**.
They wrap their entire code inside a self-executing function to isolate scope.

---

## 🧠 Understanding Closures

A closure lets a function **"remember"** its outer variables even after the outer function has returned.

```js
function greet(whatToSay) {
  return function(name) {
    console.log(whatToSay + ' ' + name);
  }
}

greet('Hi')('Kaushik'); // Hi Kaushik

var sayHi = greet('Hi');
sayHi('Kaushik'); // Hi Kaushik
```

Even though `greet()`’s execution context is gone, `sayHi()` still has access to its variables.
The function’s scope is **“closed in”** — hence the term *closure*.

---

## 🔁 Understanding Closures — Part 2

```js
function buildFunctions() {
  var arr = [];
  for (var i = 0; i < 3; i++) {
    arr.push(function() {
      console.log(i);
    });
  }
  return arr;
}

var fs = buildFunctions();
fs[0](); // 3
fs[1](); // 3
fs[2](); // 3
```

Why?
Because the loop finishes with `i = 3`, and all inner functions **reference the same `i`** variable.

### Fix with ES6 `let`

```js
function buildFunctions() {
  var arr = [];
  for (var i = 0; i < 3; i++) {
    let j = i; // creates new variable each time
    arr.push(function() {
      console.log(j);
    });
  }
  return arr;
}
```

### Fix in ES5 using IIFE

```js
function buildFunctions() {
  var arr = [];
  for (var i = 0; i < 3; i++) {
    arr.push((function(j) {
      return function() {
        console.log(j);
      }
    })(i));
  }
  return arr;
}
```

💡 **Conceptual Aside:**
This is a great example of **IIFE + closure** in action!

---

## 🧩 Framework Aside: Function Factories

A **factory** is a function that **returns or creates** other functions.

```js
function makeGreeting(language) {
  return function(firstName, lastName) {
    if (language == 'en') {
      console.log('Hello ' + firstName + ' ' + lastName);
    }
    if (language == 'es') {
      console.log('Hola! ' + firstName + ' ' + lastName);
    }
  }
}

var greetEnglish = makeGreeting('en');
var greetSpanish = makeGreeting('es');

greetEnglish('Ravi', 'Shankar');    // Hello Ravi Shankar
greetSpanish('Micheal', 'Jackson'); // Hola Micheal Jackson
```

Here:

* `greetEnglish` closes over `language = 'en'`
* `greetSpanish` closes over `language = 'es'`

Closures help you **customize and encapsulate behavior** dynamically.

---

## ⏳ Closure and Callback

```js
function sayHiLater() {
  var greeting = 'Hi';
  setTimeout(function() {
    console.log(greeting); // closure in action!
  }, 3000);
}

sayHiLater(); // Prints 'Hi' after 3 seconds
```

💡 **Conceptual Aside:**
Callbacks often **leverage closures** to access data from their enclosing scopes, even when executed asynchronously.

---

# 🧾 Summary Recap

| Concept            | Key Takeaway                                 |
| ------------------ | -------------------------------------------- |
| Arrays             | Can store mixed data types                   |
| `arguments`        | Holds all parameters passed to a function    |
| Spread (`...`)     | Packs remaining args into an array           |
| Syntax Parser      | Performs automatic semicolon insertion       |
| IIFE               | Self-executing anonymous function expression |
| Closure            | Inner function remembers its outer scope     |
| Function Factory   | Returns specialized functions (via closure)  |
| Callback + Closure | Access outer variables inside async calls    |

