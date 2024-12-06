# Javascript Closures

### Definition
A closure in JavaScript is a function that "remembers" its surrounding lexical scope even when executed outside that scope. 
It allows the function to access variables from its parent scope, even after the parent function has finished executing.

### Simple Example
```
function outerFunction() {
  let outerVariable = "I'm from the outer scope";

  return function innerFunction() {
    console.log(outerVariable); // Accessing the outer variable
  };
}

const closureFunction = outerFunction(); // outerFunction runs and returns innerFunction
closureFunction(); // Output: "I'm from the outer scope"

```

### Explanation:

- outerFunction creates a variable `outerVariable` and returns `innerFunction`.
- `innerFunction` is returned and assigned to `closureFunction`.
- The key point is
  - Even though `outerFunction` has finished execution, `closureFunction` (the inner function) still has access to `outerVariable` because of the closure.

--- 

## Challenge 1

We saw that we returned a function in previous example that had access to an outer variable. Extending on the same, 
- Please create a `count` variable and return a function that increments and returns the value of `count` everytime its invoked.

### Solution
```
function createCounter() {
  let count = 0;

  return function () {
    count++; // Modifies the outer variable `count`
    return count;
  };
}

const counter = createCounter(); // Create a new counter
console.log(counter()); // Output: 1
console.log(counter()); // Output: 2
console.log(counter()); // Output: 3
```

We can see that we are returning an anonymous function here. You can use a named function here but that won't matter!

So we could do like:
```
function createCounter() {
  let count = 0;

  return function increment() { //use a named function but that won't matter!
    count++; // Modifies the outer variable `count`
    return count;
  };
}

const counter = createCounter(); // Create a new counter
console.log(counter()); // Output: 1
console.log(counter()); // Output: 2
console.log(counter()); // Output: 3
```
So as a practice, its better to name the variable to closely represent the operation returned by the closure function.
Here it makes sense to call it `counter` as counter is usually used to increment a count.

---
## Challenge 2

Extend the previous example, now instead of just incrementing counter always, let's have the function return 3 functions which are
  - increment() : increment the counter
  - decrement() : decrement the counter
  - getCount() : get the counter value

### Solution
```
function createCounter() {
  let count = 0; // Private variable

  return {
    increment() {
      count++;
      return count;
    },
    decrement() {
      count--;
      return count;
    },
    getCount() {
      return count; // Optional: Access the current count
    }
  };
}

const counter = createCounter();

console.log(counter.increment()); // Output: 1
console.log(counter.increment()); // Output: 2
console.log(counter.decrement()); // Output: 1
console.log(counter.getCount());  // Output: 1
```

Now here functions are `first-class` objects in javascript.
so in the return we are saying:
```
return { func1, func2, func3}
```
So, it's also perfectly fine to write it as follows 

```
function createCounter() {
  
  let count = 0; // Private variable

  function increment() {
    count++;
    return count;
  }

  function decrement() {
    count--;
    return count;
  }

  function getCount() {
    return count; // Optional: Access the current count
  }
  
  return {
    increment,
    decrement,
    getCount,
  };
}

const counter = createCounter();

console.log(counter.increment()); // Output: 1
console.log(counter.increment()); // Output: 2
console.log(counter.decrement()); // Output: 1
console.log(counter.getCount());  // Output: 1
```
Choose whichever style suits you.


---

## Challenge 3

- Create a multiplier function that takes `factor` as an argument.
- Use closures where `factor` is remembered in the inner function.

### Solution

```
function multiplier(factor) {
  return function (number) {
    return number * factor; // `factor` is remembered
  };
}

const double = multiplier(2); // Creates a closure with `factor = 2`
const triple = multiplier(3); // Creates a closure with `factor = 3`

console.log(double(5)); // Output: 10
console.log(triple(5)); // Output: 15
```


### Why Are Closures Useful?

- Encapsulation: Keep variables private.
- State Management: Retain state between function calls (like counters).
- Higher-Order Functions: Return functions tailored with specific behaviors.

### Closure Side-Note

    Remember Closure remains in heap and not stack. It's long lived. So use Closures carefully.



