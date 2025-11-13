# 🧠 JavaScript Ready-Reckoner Guide

*A concise, example-driven reference for mastering Objects, Functions, JSON, and `this` behavior in JavaScript.*

---

## 🧩 Objects and Functions

In other programming languages, **objects** and **functions** are two distinct things to talk about —
but in **JavaScript**, they are **very much related**.

An **object** is a **collection of name/value pairs**.

### Creating an Object

```js
var person = new Object(); // there are better ways to do this
person["firstName"] = "Kaushik"; // string primitive
person["lastName"]  = "BK";
console.log(person);
```

**Output:**

```
{ firstName: 'Kaushik', lastName: 'BK' }
```

```js
var firstNameProperty = "firstName";
console.log(person[firstNameProperty]);
```

**Output:**

```
Kaushik
```

✅ You’ll sometimes see this form in frameworks because it allows **dynamic property access**.

---

### Dot Notation (Preferred)

```js
console.log(person.firstName);
```

**Output:**

```
Kaushik
```

### Nested Objects

```js
person.address = new Object();
person.address.street = "BG Road";
person.address.city   = "Bengaluru";
person.address.state  = "KA";

console.log(person.address.street);
console.log(person.address.city);
console.log(person["address"]["state"]);
```

**Output:**

```
BG Road
Bengaluru
KA
```

> ⚠️ **Note:** This is *not* the preferred way to create an object.
> Prefer **object literals** and the `.` operator.

---

## 🧱 Objects and Object Literals

In JavaScript, there are often more than one way to do something.

### Object Literal Syntax

```js
var person = {}; // same as new Object()
```

### Inline Initialization

```js
var person = { firstName: 'Kaushik', lastName: 'BK' };
console.log(person);
```

**Output:**

```
{ firstName: 'Kaushik', lastName: 'BK' }
```

### Nested Object Example

```js
var person = {
  firstName: 'Kaushik',
  lastName: 'BK',
  address: {
    street: 'BG Road',
    city:   'Bengaluru',
    state:  'KA'
  }
};
```

---

### Passing Objects to Functions

```js
function greet(person) {
  console.log('Hi ' + person.firstName);
}

greet(person);
greet({ firstName: 'Micheal', lastName: 'Jackson' });
```

**Output:**

```
Hi Kaushik
Hi Micheal
```

> A function can receive an object created *on the fly*.

---

## 🗂️ Framework Aside: Faking Namespaces

A **namespace** is a container for variables and functions —
typically used to **prevent naming collisions**.

### Problem

```js
var greet = "Hello";
var greet = "Hola!";
console.log(greet);
```

**Output:**

```
Hola!
```

Imagine these two variables were in different JS files (English vs Spanish).
They overwrite each other.

---

### Solution: Use Namespace Objects

```js
var english = {};
var spanish = {};

english.greet = "Hello!";
spanish.greet = "Hola!";

console.log(english.greet);
console.log(spanish.greet);
```

**Output:**

```
Hello!
Hola!
```

Nested version:

```js
var english = { greetings: { greet: "Hello" } };
console.log(english.greetings.greet);
```

**Output:**

```
Hello
```

✅ Group variables/functions into container objects to avoid collisions.

---

## 🌐 JSON and Object Literals

**JSON: JavaScript Object Notation**

It is **inspired by JavaScript Object Literal Syntax.**

### Concept

JSON is a **lightweight, text-based data format** used for storing and transmitting structured data.
It was inspired by JS object syntax and later standardized for data exchange across languages.
Historically, **data was sent as XML**, which was verbose and harder to parse.

---

### Example

```js
var objectLiteral = { 
  firstName: 'Ravi',
  isMusician: true
};
console.log(objectLiteral);
```

**Output:**

```
{ firstName: 'Ravi', isMusician: true }
```

### Equivalent JSON Representation

```json
{
  "firstName": "Ravi",
  "isMusician": true
}
```

> ✅ In JSON, property names **must be enclosed in double quotes**.

---

### Conversion Between JSON and JS Objects

Convert object → JSON string:

```js
console.log(JSON.stringify(objectLiteral));
```

**Output:**

```
{"firstName":"Ravi","isMusician":true}
```

Convert JSON string → object:

```js
var jsonValue = JSON.parse('{ "firstName":"Ravi", "isMusician":true }');
console.log(jsonValue);
```

**Output:**

```
{ firstName: 'Ravi', isMusician: true }
```

✅ `JSON.stringify()` converts an object to JSON text.
✅ `JSON.parse()` converts a JSON string back into a JS object.

---

## ⚙️ Functions Are Objects

Everything you can do with other types (objects, strings, numbers), you can also do with **functions**:
assign them to variables, pass them around, or create them on the fly.

Functions are a **special type of object** with:

* a **Name** (optional)
* **Invocable code** (hidden property)
* **Other properties** (can be primitives, objects, or functions)

---

### Example

```js
function greet() {
  console.log('Hi');
}
greet.language = 'english';
console.log(greet.language);
```

**Output:**

```
english
```

> The function itself is an object; the code you write is just its **invocable property**.

---

## 🧾 Function Statements and Function Expressions

### Definition: Expression

> A unit of code that results in a **value**.
> It doesn’t have to be stored in a variable.

```js
a = 3; 
1 + 2;
a = { greeting: 'hi' };
```

---

### Definition: Function Statement

> A function defined using the `function` keyword in the standard way.
> **Hoisted** — placed into memory during creation phase.

```js
greet();
function greet() {
  console.log('Hi');
}
```

**Output:**

```
Hi
```

---

### Definition: Function Expression

> A function created as part of an expression and assigned to a variable.
> **Not hoisted** — must be defined before use.

```js
var anonymousGreet = function() {
  console.log('Hi');
};
anonymousGreet();
```

**Output:**

```
Hi
```

### ❌ Calling Before Definition

```js
anonymousGreet();
var anonymousGreet = function() {
  console.log('Hi');
};
```

**Output:**

```
Uncaught ReferenceError: anonymousGreet is not defined
```

> Because the variable `anonymousGreet` is not yet defined in memory.

---

### Passing Functions as Arguments

```js
function log(a) {
  console.log(a);
}

log(3);
log('Hello');
log({ greeting: 'Hi' });
log(function(){ console.log('Hi'); });
```

**Output:**

```
3
Hello
{ greeting: 'Hi' }
ƒ (){ console.log('Hi'); }
```

Invoke the function argument:

```js
function log(a) {
  a();
}
log(function(){ console.log('Hi'); });
```

**Output:**

```
Hi
```

---

## 💡 Conceptual Aside: By Value vs By Reference

When assigning or passing values:

* **Primitives** → passed **by value**
* **Objects** → passed **by reference**

### By Value

```js
var a = 3;
var b = a;
a = 2;
console.log(a);
console.log(b);
```

**Output:**

```
2
3
```

### By Reference

```js
var c = { greeting: 'Hi' };
var d = c;
c.greeting = 'Hello';
console.log(c);
console.log(d);
```

**Output:**

```
{ greeting: 'Hello' }
{ greeting: 'Hello' }
```

Function example:

```js
function changeGreeting(obj) {
  obj.greeting = 'Hola!';
}
changeGreeting(d);
console.log(c);
console.log(d);
```

**Output:**

```
{ greeting: 'Hola!' }
{ greeting: 'Hola!' }
```

Assigning a **new object** creates a new memory reference:

```js
c = { greeting: 'Howdy' };
console.log(c);
console.log(d);
```

**Output:**

```
{ greeting: 'Howdy' }
{ greeting: 'Hola!' }
```

---

## 🔍 The `this` Keyword

`this` refers to **the object that owns the current execution context.**

### Global Context

```js
console.log(this);
```

**Output (browser):**

```
Window { ... }
```

---

### Inside a Function

```js
function a() {
  console.log(this);
}
a();
```

**Output:**

```
Window { ... }
```

Even function expressions:

```js
var b = function() {
  console.log(this);
}
b();
```

**Output:**

```
Window { ... }
```

> In non-strict mode, top-level `this` refers to the **global object** (`window`).
> In strict mode, it is **`undefined`**.

---

### Strange Behavior: Global Variable Creation

```js
function a() {
  console.log(this);
  this.newVariable = 'hello';
}
a();
console.log(newVariable);
```

**Output:**

```
Window { ... }
hello
```

---

### Inside Object Methods

When a function is called as a **method**, `this` refers to the **object that owns it**.

```js
var c = {
  name: 'The C object',
  log: function() {
    console.log(this);
  }
};
c.log();
```

**Output:**

```
{ name: 'The C object', log: ƒ }
```

---

### Modifying Object Using `this`

```js
var c = {
  name: 'The C object',
  log: function() {
    this.name = 'Updated C object';
    console.log(this);
  }
};
c.log();
```

**Output:**

```
{ name: 'Updated C object', log: ƒ }
```

---

### ❌ Problem: Losing `this` in Inner Functions

```js
var c = {
  name: 'The C object',
  log: function() {
    this.name = 'Updated C object';
    var setname = function(newname) {
      this.name = newname;
    };
    setname('updated again! the c object!');
    console.log(this);
  }
};
c.log();
```

**Output:**

```
{ name: 'Updated C object', log: ƒ }
```

And in the global scope:

```
Window.name = 'updated again! the c object!'
```

> In **non-strict mode**, a standalone inner function’s `this` defaults to the **global object**.
> In **strict mode**, it becomes **`undefined`**.

---

### ✅ Solution: Capture `this` Using `self`

```js
var c = {
  name: 'The C object',
  log: function() {
    var self = this;
    self.name = 'Updated C object';
    var setname = function(newname) {
      self.name = newname;
    };
    setname('updated again! the c object!');
    console.log(this);
  }
};
c.log();
```

**Output:**

```
{ name: 'updated again! the c object!', log: ƒ }
```

✅ The variable `self` preserves the original object reference correctly.

---

## 🧭 Summary Table

| Concept                   | Definition / Description                                                              |
| ------------------------- | ------------------------------------------------------------------------------------- |
| **Object**                | A collection of name/value pairs                                                      |
| **Object Literal**        | Preferred, concise syntax for creating objects                                        |
| **JSON**                  | JavaScript Object Notation — a lightweight text format inspired by JS object literals |
| **Function Statement**    | Declared function that is hoisted                                                     |
| **Function Expression**   | Function assigned to variable; not hoisted                                            |
| **Functions as Objects**  | Functions are special objects with invocable code and properties                      |
| **By Value**              | Primitives are copied by value                                                        |
| **By Reference**          | Objects share memory; changes affect all references                                   |
| **`this` (Global)**       | Refers to the global object (`window` in browsers)                                    |
| **`this` (Strict Mode)**  | Undefined when not bound explicitly                                                   |
| **`this` (Method)**       | Refers to the object that owns the method                                             |
| **Inner Function `this`** | Defaults to global (non-strict) or undefined (strict)                                 |
| **Fix for `this` Loss**   | Use `var self = this` (or arrow functions in ES6)                                     |
| **Namespace**             | Object used to group variables/functions and prevent collisions                       |

