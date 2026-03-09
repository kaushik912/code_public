#### **Example: Non-Blocking Execution**
```java
import java.util.concurrent.*;

public class CompletableFutureCallbackExample {
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(3);

        // Start an asynchronous expensive calculation
        CompletableFuture<Integer> futureResult = CompletableFuture.supplyAsync(() -> expensiveCalculation(), executor);

        // Attach a callback to be executed when the computation is complete
        futureResult.thenAccept(result -> {
            System.out.println("Expensive calculation completed. Result: " + result);
        });

        // Continue doing other tasks while the calculation is running
        System.out.println("Main thread is free to do other work...");

        // Shutdown the executor gracefully
        executor.shutdown();
    }

    public static int expensiveCalculation() {
        try {
            System.out.println("Performing an expensive computation...");
            Thread.sleep(3000); // Simulating delay
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return 42; // Return some computed result
    }
}
```


---

### **🔹 How This Works**
✅ **Non-blocking**: `thenAccept()` registers a callback instead of blocking the main thread.  
✅ **Callback triggers automatically** when `expensiveCalculation()` is done.  
✅ **Main thread remains free** for other work.  

---

### **🔹 Alternative: Transforming the Result with `thenApply()`**
If you want to process the result and return another computed value, use `thenApply()`:

```java
futureResult.thenApply(result -> "Final Computed Value: " + (result * 2))
            .thenAccept(System.out::println);
```

---

### **🔹 Want to Combine Multiple Futures?**
If you have **multiple tasks** that depend on each other, use `thenCombine()`:
```java
CompletableFuture<Integer> future1 = CompletableFuture.supplyAsync(() -> 10);
CompletableFuture<Integer> future2 = CompletableFuture.supplyAsync(() -> 20);

future1.thenCombine(future2, Integer::sum)
       .thenAccept(sum -> System.out.println("Sum of results: " + sum));
```

---

### **When does `executor.shutdown()` execute?**
1. **Main thread starts execution.**  
2. **Two `CompletableFuture` tasks (`fetchStockPrice` & `fetchStockNews`) are submitted to the executor.**  
3. **`thenCombine()` schedules the combination task** (which runs once both tasks complete).  
4. **`thenAccept()` schedules a callback** to print the result.  
5. **Main thread reaches `executor.shutdown()` and shuts down the executor.**  
6. **Executor will NOT accept new tasks, but it allows running tasks to complete.**  
7. **The `thenAccept()` callback runs when both async tasks are done, even after shutdown.**  
