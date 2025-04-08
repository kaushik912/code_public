### **Example Code: Fetch Stock Prices and News in Parallel**  
```java
import java.util.concurrent.*;

public class StockDashboard {
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(2);

        // Fetch stock price asynchronously
        CompletableFuture<String> stockPriceFuture = CompletableFuture.supplyAsync(() -> fetchStockPrice("AAPL"), executor);

        // Fetch latest news asynchronously
        CompletableFuture<String> newsFuture = CompletableFuture.supplyAsync(() -> fetchStockNews("AAPL"), executor);

        // Combine both results
        CompletableFuture<String> combinedFuture = stockPriceFuture.thenCombine(newsFuture, (price, news) -> {
            return "📈 " + price + "\n📰 " + news;
        });

        // Display the result when both are ready
        combinedFuture.thenAccept(System.out::println);

        // Shutdown executor gracefully
        executor.shutdown();
    }

    // Simulate fetching stock price (e.g., API call)
    public static String fetchStockPrice(String stock) {
        try {
            Thread.sleep(2000); // Simulating delay
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return "AAPL Price: $150.75";
    }

    // Simulate fetching latest stock-related news
    public static String fetchStockNews(String stock) {
        try {
            Thread.sleep(1500); // Simulating delay
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return "Apple releases new MacBooks!";
    }
}
```

---

### **Expected Output (after ~2 sec delay)**  
```
📈 AAPL Price: $150.75
📰 Apple releases new MacBooks!
```

---

### **Why Use `thenCombine()`?**  
✅ **Runs independently in parallel** – Stock price and news fetch do not block each other.  
✅ **Combines results elegantly** – No need for waiting manually.  
✅ **Better performance** – Faster than fetching sequentially.  

---

### **Will the program terminate before `thenAccept()` runs?**
**No**, because:
- `shutdown()` only prevents **new tasks** from being submitted.  
- It **waits** for already running tasks (`fetchStockPrice`, `fetchStockNews`, and their `thenCombine()` task) to complete.  
- Since `thenAccept()` is scheduled as part of the `thenCombine()`, it still gets executed.

---

### **How to Ensure Completion Before Shutdown?**
To **guarantee** that all tasks finish before shutdown, you can use:
```java
executor.shutdown();
try {
    executor.awaitTermination(5, TimeUnit.SECONDS); // Wait for all tasks to finish
} catch (InterruptedException e) {
    e.printStackTrace();
}
```
This will **block** the main thread until all tasks are done, avoiding premature termination.
