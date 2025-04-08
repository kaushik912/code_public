### **Requirement: Asynchronous Computation with Callback using `CompletableFuture`**  

#### **Objective:**  
Develop a Java program that performs an expensive computation asynchronously using `CompletableFuture` while allowing the main thread to continue executing other tasks. The result of the computation should be handled via a callback.

#### **Functional Requirements:**  
1. The system should execute an **expensive computation** asynchronously using a separate thread pool.  
2. The computation should take approximately **3 seconds** to simulate a long-running task.  
3. The system should **use a fixed thread pool** with **3 threads** for executing the computation.  
4. The main thread should remain free to perform **other operations** while the computation runs.  
5. Once the computation completes, a **callback function** should print the result in the format:  
   ```
   Expensive calculation completed. Result: <computed_value>
   ```
6. The main thread should indicate that it is free by printing:  
   ```
   Main thread is free to do other work...
   ```
7. The system should ensure **graceful shutdown** of the thread pool after the computation starts.

#### **Non-Functional Requirements:**  
- The solution should be **non-blocking**, ensuring that the main thread is not waiting for the computation to finish.  
- The system should be **scalable**, capable of handling multiple asynchronous computations if extended.  
- Proper **exception handling** should be included to manage potential interruptions in the computation.  

#### **Constraints:**  
- The computation method must return a fixed value (`42`) as a placeholder for an actual expensive operation.  
- The delay should be simulated using `Thread.sleep(3000)` within the computation method.  
- The implementation should use `CompletableFuture.supplyAsync()` to trigger asynchronous execution.  
