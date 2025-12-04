# 🧠 JavaScript Closures — A Deep Dive

### 💡 Definition

A **closure** in JavaScript is when a function "remembers" the variables from its **lexical scope** (the environment where it was created) even after that outer function has finished executing.

> In short: **A closure gives you access to an outer function’s variables from an inner function**, even after the outer function is done running.

---

## 🔍 Simple Example

```js
function outerFunction() {
  let outerVariable = "I'm from the outer scope";

  return function innerFunction() {
    console.log(outerVariable); // Accessing the outer variable
  };
}

const closureFunction = outerFunction(); // outerFunction runs and returns innerFunction
closureFunction(); // Output: "I'm from the outer scope"
```

### 🧩 Explanation

* `outerFunction` creates a variable `outerVariable` and returns `innerFunction`.
* When we call `outerFunction()`, it returns the **inner function**.
* Even though `outerFunction` is done executing, `innerFunction` still has access to `outerVariable` — thanks to **closure**!

Think of it like this:

> The inner function “packs a backpack” with all the variables it needs before leaving the outer function.

---

## ⚙️ Challenge 1 — The Counter

We saw how closures can remember variables.
Let’s now make a simple **counter** that keeps track of how many times it’s called.

### ✅ Solution 1 — Using Anonymous Function

```js
function createCounter() {
  let count = 0;

  return function () {
    count++; // modifies outer variable
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3
```

### ✅ Solution 2 — Using Named Function

(Naming makes debugging easier)

```js
function createCounter() {
  let count = 0;

  return function increment() {
    count++;
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3
```

### ⚡ ES6 Arrow Function Version

```js
const createCounter = () => {
  let count = 0;
  return () => ++count;
};

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
```

🧠 **Tip:** Name the variable to reflect the operation it performs — `counter` makes perfect sense here!

---

## ⚙️ Challenge 2 — Increment, Decrement, Get Count

Let’s upgrade our counter.
We’ll return **three functions** — `increment`, `decrement`, and `getCount`.

### ✅ Solution 1 — Inline Object

```js
function createCounter() {
  let count = 0; // Private variable

  return {
    increment() {
      return ++count;
    },
    decrement() {
      return --count;
    },
    getCount() {
      return count;
    }
  };
}

const counter = createCounter();

console.log(counter.increment()); // 1
console.log(counter.increment()); // 2
console.log(counter.decrement()); // 1
console.log(counter.getCount());  // 1
```

### ✅ Solution 2 — Define Functions First

```js
function createCounter() {
  let count = 0;

  function increment() { return ++count; }
  function decrement() { return --count; }
  function getCount() { return count; }

  return { increment, decrement, getCount };
}

const counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.decrement()); // 0
```

### ⚡ Arrow Function Version

```js
const createCounter = () => {
  let count = 0;
  const increment = () => ++count;
  const decrement = () => --count;
  const getCount = () => count;
  return { increment, decrement, getCount };
};
```

> Here, closures make `count` **private** — nothing outside `createCounter` can directly modify it.

---

## 🧮 Challenge 3 — The Multiplier Factory

Let’s make a **function factory** that “remembers” a factor and returns a function that multiplies any number by it.

### ✅ Solution

```js
function multiplier(factor) {
  return function (number) {
    return number * factor; // closure remembers factor
  };
}

const double = multiplier(2);
const triple = multiplier(3);

console.log(double(5)); // 10
console.log(triple(5)); // 15
```

### ⚡ Arrow Function Version

```js
const multiplier = (factor) => (number) => number * factor;

const double = multiplier(2);
const triple = multiplier(3);

console.log(double(4)); // 8
console.log(triple(4)); // 12
```

> The inner arrow function captures `factor` — that’s closure magic in one line!

---

## 🧰 Higher-Order Function Challenge — Dynamic Filters

A client wants reusable filters for arrays:

* `isEven`
* `isOdd`
* `isGreaterThanFive`

We’ll use **higher-order functions** and **closures** to make this elegant.

### ✅ Solution

```js
function createFilter(condition) {
  return function (array) {
    return array.filter(condition); // closure captures condition
  };
}

// Create specific filters
const isEven = createFilter(num => num % 2 === 0);
const isOdd = createFilter(num => num % 2 !== 0);
const isGreaterThanFive = createFilter(num => num > 5);

// Use them
const numbers = [1, 2, 3, 4, 5, 6, 7, 8];
console.log(isEven(numbers));           // [2, 4, 6, 8]
console.log(isOdd(numbers));            // [1, 3, 5, 7]
console.log(isGreaterThanFive(numbers));// [6, 7, 8]
```

### ⚡ Arrow Function Version

```js
const createFilter = (condition) => (array) => array.filter(condition);

const isEven = createFilter(n => n % 2 === 0);
const isOdd = createFilter(n => n % 2 !== 0);
const isGreaterThanFive = createFilter(n => n > 5);
```

> Each filter “remembers” its unique `condition` function — that’s closure power in functional programming.

---

## 🎯 Why Are Closures Useful?

| Purpose                           | Description                                                 |
| --------------------------------- | ----------------------------------------------------------- |
| 🧱 **Encapsulation**              | Keep variables private and safe from external modification. |
| 🔁 **State Management**           | Maintain state between function calls (like counters).      |
| ⚙️ **Custom Function Generation** | Create tailored, reusable functions dynamically.            |

---

## ⚠️ Closure Side-Note

Closures **live on the heap**, not the stack.
They persist as long as the returned function exists.
So, be mindful — **excessive or unintended closures** can lead to **memory leaks**.

---

### 🔚 Final Thought

> Closures are like a “time capsule” — your inner function carries a snapshot of the environment it was born in.
> Master them, and you master the soul of JavaScript.


