# 🚀 Modern JavaScript Cheat Sheet

*A quick reference for learners, interview prep & React developers*

---

## ✨ 1. Variables

| Old JS        | Modern JS       | Notes                |
| ------------- | --------------- | -------------------- |
| `var x = 10;` | `let x = 10;`   | Block-scoped, safer  |
| `var y = 20;` | `const y = 20;` | Prevent reassignment |

✔ **Avoid `var` completely** unless maintaining legacy code.

---

## ✨ 2. Functions (Anonymous → Arrow)

**Old:**

```js
const add = function(a, b) {
  return a + b;
};
```

**New:**

```js
const add = (a, b) => a + b;
```

**When *not* to use arrow functions:**

* When you need your own `this`
* When using constructors
* When needing `arguments`

---

## ✨ 3. IIFE → ES Modules

**Old (IIFE for private scope):**

```js
const Counter = (function() {
  let count = 0;
  return {
    inc() { count++ },
    get() { return count }
  };
})();
```

**New (Modules automatically give private scope):**

**counter.js**

```js
let count = 0;
export function inc() { count++; }
export function get() { return count; }
```

**main.js**

```js
import { inc, get } from './counter.js';
```

✔ No need for IIFE in modern JS unless for interview demos.

---

## ✨ 4. Prototype Inheritance → ES6 Classes

**Old:**

```js
function Person(name) {
  this.name = name;
}
Person.prototype.sayHi = function() {
  console.log("Hi " + this.name);
};
```

**New:**

```js
class Person {
  constructor(name) {
    this.name = name;
  }

  sayHi() {
    console.log(`Hi ${this.name}`);
  }
}
```

✔ Cleaner
✔ Familiar to Java/C++ developers
✔ Used in React class components (legacy)

---

## ✨ 5. Object Literals (Old Verbose → New Shorthand)

**Old:**

```js
const name = "John";
const user = { name: name, sayHi: function() { console.log("Hi"); } };
```

**New:**

```js
const name = "John";
const user = {
  name,
  sayHi() {
    console.log("Hi");
  }
};
```

---

## ✨ 6. Callbacks → Promises → async/await

**Old (callback hell):**

```js
doTask(function(result) {
  nextTask(result, function(final) {
    console.log(final);
  });
});
```

**Modern:**

```js
const result = await doTask();
console.log(result);
```

✔ React code rarely uses callbacks now
✔ `async/await` is the standard for API calls

---

## ✨ 7. for loops → Array methods

**Old:**

```js
for (var i = 0; i < nums.length; i++) {
  console.log(nums[i] * 2);
}
```

**New:**

```js
nums.map(n => n * 2);
```

✔ Declarative
✔ Functional style (React-friendly)

---

## ✨ 8. XHR → Fetch API

**Old:**

```js
var xhr = new XMLHttpRequest();
xhr.open('GET', '/api');
xhr.onload = () => console.log(xhr.response);
xhr.send();
```

**New:**

```js
const data = await fetch('/api').then(res => res.json());
```

---

## ✨ 9. `arguments` → Rest operator

**Old:**

```js
function sum() {
  return Array.prototype.reduce.call(arguments, (a,b) => a+b);
}
```

**New:**

```js
const sum = (...nums) => nums.reduce((a,b) => a+b);
```

---

## ✨ 10. String concatenation → Template literals

**Old:**

```js
const msg = "Hello " + name + "!";
```

**New:**

```js
const msg = `Hello ${name}!`;
```

---

## ✨ 11. Default parameters

**Old:**

```js
function greet(name) {
  name = name || "Guest";
  console.log("Hi " + name);
}
```

**New:**

```js
function greet(name = "Guest") {
  console.log(`Hi ${name}`);
}
```

---

## ✨ 12. Object.assign → Spread operator

**Old:**

```js
const newObj = Object.assign({}, obj, { age: 20 });
```

**New:**

```js
const newObj = { ...obj, age: 20 };
```

---

## ✨ 13. Manual binding of `this` → Arrow functions in React

**Old (React class):**

```js
this.handleClick = this.handleClick.bind(this);
```

**New (React functional):**

```jsx
<button onClick={() => setCount(c + 1)}>+</button>
```

✔ No binding
✔ No class components
✔ Recommended

---

## ✨ 14. Modules: `require()` → `import/export`

**Old (CommonJS):**

```js
const fs = require("fs");
module.exports = something;
```

**New (ES Modules):**

```js
import fs from "fs";
export default something;
```

---

## ✨ 15. `Math.pow` → Exponent operator

```
Math.pow(2, 3)   // old
2 ** 3           // new
```

---

## ✨ 16. Manual property checks → Optional chaining

**Old:**

```js
if (user && user.address && user.address.city) {
  console.log(user.address.city);
}
```

**New:**

```js
console.log(user?.address?.city);
```

---

## 🎉 Final Summary Table

| Purpose       | Old JS     | Modern JS          |
| ------------- | ---------- | ------------------ |
| Scope         | `var`      | `let`, `const`     |
| Encapsulation | IIFE       | Modules            |
| OOP           | Prototype  | Classes            |
| Async         | Callbacks  | Promises / async   |
| Functions     | Anonymous  | Arrow functions    |
| Strings       | `+` concat | Template literals  |
| Arrays        | For loops  | `map`, `filter`    |
| Imports       | `require`  | `import/export`    |
| API calls     | XHR        | Fetch              |
| Private data  | Closures   | Modules + Closures |

---


