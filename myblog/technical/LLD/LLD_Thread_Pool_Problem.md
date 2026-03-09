### **Java Design Challenge: Implement a Thread Pool Using Design Patterns**  

#### **Objective:**  
Design and implement a custom **Thread Pool** that efficiently manages a pool of worker threads to execute submitted tasks. The solution should demonstrate knowledge of **design patterns** such as:  
- **Singleton Pattern** (Ensuring a single instance of the thread pool)  
- **Factory Pattern** (Creating worker threads)  
- **Producer-Consumer Pattern** (Managing task submission and execution)  
- **Strategy Pattern** (Supporting different task scheduling strategies)  

---

### **Requirements:**  
1. **Thread Pool Management:**  
   - Maintain a fixed number of worker threads.  
   - Reuse existing threads instead of creating new ones.  
   - Allow dynamic resizing of the thread pool.  

2. **Task Execution:**  
   - Provide a method to submit tasks to the pool.  
   - Use a queue to hold pending tasks (BlockingQueue).  
   - Ensure efficient task execution using worker threads.  

3. **Graceful Shutdown:**  
   - Implement a mechanism to stop accepting new tasks.  
   - Ensure that ongoing tasks complete execution before shutdown.  

4. **Concurrency Handling:**  
   - Ensure thread safety when managing the task queue.  
   - Implement proper synchronization mechanisms to prevent race conditions.  

5. **Flexible Task Scheduling (Optional Advanced Feature):**  
   - Use a **Strategy Pattern** to allow different scheduling policies (e.g., FIFO, priority-based execution).  

---
