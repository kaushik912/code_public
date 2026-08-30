### **Requirement Document: Asynchronous Stock Dashboard**  

#### **Objective:**  
Develop a Java-based stock dashboard that fetches real-time stock prices and related news asynchronously using `CompletableFuture`. The system should efficiently combine and display the results while allowing concurrent execution.  

---

### **Functional Requirements:**  
1. The system should fetch **stock price data** asynchronously for a given stock symbol (e.g., `"AAPL"`).  
2. The system should fetch **latest stock-related news** asynchronously for the same stock symbol.  
3. Both operations should execute in parallel using a **fixed thread pool** with **2 threads** to optimize resource utilization.  
4. Once both the stock price and news are retrieved, the system should:  
   - **Combine** the results in the following format:  
     ```
     📈 AAPL Price: $150.75
     📰 Apple releases new MacBooks!
     ```
   - **Display the combined output** when both results are available.  
5. The program should ensure a **graceful shutdown** of the executor service after initiating the tasks.  

---

### **Non-Functional Requirements:**  
- **Concurrency:** The system must use `CompletableFuture` to execute tasks asynchronously without blocking the main thread.  
- **Performance:** Fetching stock price and news should happen in parallel to reduce overall execution time.  
- **Scalability:** The implementation should support easy extension to fetch additional stock-related data.  
- **Resilience:** The system should handle potential interruptions during data fetching (e.g., using exception handling).  

---

### **Constraints:**  
- The stock price fetching method should **simulate a 2-second delay** (`Thread.sleep(2000)`).  
- The news fetching method should **simulate a 1.5-second delay** (`Thread.sleep(1500)`).  
- A fixed stock symbol (`"AAPL"`) should be used in the implementation for demonstration purposes.  
- The `Executors.newFixedThreadPool(2)` should be used to limit thread pool size to 2 threads.  
- The implementation should use `CompletableFuture.supplyAsync()` for asynchronous execution and `thenCombine()` to merge results.  
