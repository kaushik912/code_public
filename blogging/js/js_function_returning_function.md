# Functions returning Functions

Yes! In javascript, we can return mutliple functions from a function.
Read below to learn more..

## Methods to Return Multiple Functions
- Using an Object
- Using an Array
- Using an Immediately Invoked Function Expression (IIFE)
- Using Classes

# Using an Object
Returning an object is the most common and flexible way to return multiple functions. 
Each function is assigned as a property of the object, allowing you to access them using dot notation or destructuring.

```
function createMathOperations() {
  function add(a, b) {
    return a + b;
  }

  function subtract(a, b) {
    return a - b;
  }

  function multiply(a, b) {
    return a * b;
  }

  function divide(a, b) {
    if (b === 0) {
      throw new Error("Cannot divide by zero.");
    }
    return a / b;
  }

  return {
    add,
    subtract,
    multiply,
    divide
  };
}

const mathOps = createMathOperations();

console.log(mathOps.add(5, 3));      // Output: 8
console.log(mathOps.subtract(5, 3)); // Output: 2
console.log(mathOps.multiply(5, 3)); // Output: 15
console.log(mathOps.divide(6, 3));   // Output: 2

```
### Challenge 
Re-write the above code using arrow functions.

### Solution
```
const createMathOperations = () => {
  const add = (a, b) => a + b;

  const subtract = (a, b) => a - b;

  const multiply = (a, b) => a * b;

  const divide = (a, b) => {
    if (b === 0) {
      throw new Error("Cannot divide by zero.");
    }
    return a / b;
  };

  return {
    add,
    subtract,
    multiply,
    divide,
  };
};
const mathOps = createMathOperations();

console.log(mathOps.add(5, 3));      // Output: 8
console.log(mathOps.subtract(5, 3)); // Output: 2
console.log(mathOps.multiply(5, 3)); // Output: 15
console.log(mathOps.divide(6, 3));   // Output: 2
```

Again choose whichever style suits you.

# Using an Array
Return multiple functions as an array!
While less common than using objects, you can also return multiple functions within an array. 
This method is suitable when the order of functions is important or when dealing with a list of similar functions.

Sample example would be to give some callback functions.
```
function createCallbacks() {
  function onSuccess(message) {
    console.log("Success:", message);
  }

  function onError(error) {
    console.error("Error:", error);
  }

  return [onSuccess, onError];
}

const [successCallback, errorCallback] = createCallbacks();

successCallback("Data loaded successfully."); // Output: Success: Data loaded successfully.
errorCallback("Failed to load data.");        // Output: Error: Failed to load data.

```
Note: we are using array-destructing here to assign the functions to `successCallback` and `errorCallback`. So order matters!

# Using an Immediately Invoked Function Expression (IIFE)
An IIFE can return multiple functions by encapsulating them within its scope. 
This approach is useful for creating `modules` with private and public functions.

```
const userModule = (function () {
  let userCount = 0; // Private variable

  function addUser(name) {
    userCount++;
    console.log(`User ${name} added. Total users: ${userCount}`);
  }

  function removeUser(name) {
    if (userCount > 0) {
      userCount--;
      console.log(`User ${name} removed. Total users: ${userCount}`);
    } else {
      console.log("No users to remove.");
    }
  }

  function getUserCount() {
    return userCount;
  }

  return {
    addUser,
    removeUser,
    getUserCount
  };
})();

userModule.addUser("Alice");    // Output: User Alice added. Total users: 1
userModule.addUser("Bob");      // Output: User Bob added. Total users: 2
userModule.removeUser("Alice"); // Output: User Alice removed. Total users: 1
console.log(userModule.getUserCount()); // Output: 1

```
- IIFE Structure:
  - The function is defined and immediately invoked.
  - `userCount` is a `private` variable, not accessible outside the IIFE.
- Returned Object:
  - Returns an object containing the functions `addUser`, `removeUser`, and `getUserCount`.
  - These functions have access to the `private` `userCount` variable via closure.
- Using the Module:
  - Interacts with the module using `userModule`.`addUser`, `userModule`.`removeUser`, and `userModule`.`getUserCount`.

Use IIFE for `singleton` kind of scenarios ie. when you want to run some initialization code only once.


# Using Classes

JavaScript's class syntax allows you to define multiple methods within a class, which can be instantiated to create objects containing these methods.

```
class Logger {
  constructor() {
    this.logs = [];
  }

  log(message) {
    this.logs.push(`LOG: ${message}`);
    console.log(`LOG: ${message}`);
  }

  error(message) {
    this.logs.push(`ERROR: ${message}`);
    console.error(`ERROR: ${message}`);
  }

  getLogs() {
    return this.logs;
  }
}

const logger = new Logger();

logger.log("Application started."); // Output: LOG: Application started.
logger.error("An unexpected error occurred."); // Output: ERROR: An unexpected error occurred.
console.log(logger.getLogs()); // Output: ["LOG: Application started.", "ERROR: An unexpected error occurred."]

```
### Challenge 

Write a function that returns multiple functions for a banking service.
- There should be a private variable `balance` that shouldn't be accessible from outside.
- The functions you need to return are: `deposit`, `withdraw`,`getBalance` 

### Solution

```
function createBankAccount(initialBalance = 0) {
  let balance = initialBalance; // Private variable

  function deposit(amount) {
    if (amount > 0) {
      balance += amount;
      console.log(`Deposited: $${amount}. New Balance: $${balance}`);
    } else {
      console.log("Deposit amount must be positive.");
    }
  }

  function withdraw(amount) {
    if (amount > 0 && amount <= balance) {
      balance -= amount;
      console.log(`Withdrew: $${amount}. New Balance: $${balance}`);
    } else {
      console.log("Invalid withdrawal amount.");
    }
  }

  function getBalance() {
    console.log(`Current Balance: $${balance}`);
    return balance;
  }

  return {
    deposit,
    withdraw,
    getBalance
  };
}

const myAccount = createBankAccount(100);

myAccount.deposit(50);    // Output: Deposited: $50. New Balance: $150
myAccount.withdraw(30);   // Output: Withdrew: $30. New Balance: $120
myAccount.getBalance();   // Output: Current Balance: $120
myAccount.withdraw(200);  // Output: Invalid withdrawal amount.
myAccount.getBalance();   // Output: Current Balance: $120

```

## Benefits of Returning Multiple Functions

### Encapsulation:
Keeps related functionalities bundled together.
Protects private data by exposing only necessary functions.

### Modularity:
Promotes code reusability and separation of concerns.
Makes the codebase easier to maintain and understand.

### Flexibility:
Allows consumers of the functions to use only the parts they need.
Facilitates the creation of customizable and dynamic behaviors.

### Namespace Management:
Reduces global scope pollution by grouping functions within objects or modules.

 
 
