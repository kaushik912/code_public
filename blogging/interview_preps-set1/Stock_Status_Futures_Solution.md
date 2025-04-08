### Stock Status Futures Solution
```java
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

class StockStats {
    private double minPrice;
    private double maxPrice;
    private double averagePrice;

    public StockStats(double min, double max, double avg) {
        this.minPrice = min;
        this.maxPrice = max;
        this.averagePrice = avg;
    }

    @Override
    public String toString() {
        return String.format("Min: %.2f, Max: %.2f, Avg: %.2f", minPrice, maxPrice, averagePrice);
    }
}

public class StockPriceAnalyzer {
    private static final int THREAD_COUNT = 4;
    
    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        Map<String, List<Double>> stockPrices = new ConcurrentHashMap<>();
        List<Future<Map<String, StockStats>>> futures = new ArrayList<>();

        // Read file and parse stock prices
        try (BufferedReader reader = new BufferedReader(new FileReader("stocks.txt"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length != 2) continue;

                String stock = parts[0].trim();
                double price = Double.parseDouble(parts[1].trim());

                stockPrices.computeIfAbsent(stock, k -> Collections.synchronizedList(new ArrayList<>())).add(price);
            }
        }

        // Submit tasks for each stock to calculate min, max, and average price
        for (String stock : stockPrices.keySet()) {
            List<Double> prices = stockPrices.get(stock);
            futures.add(executor.submit(() -> {
                double min = Collections.min(prices);
                double max = Collections.max(prices);
                double avg = prices.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);

                Map<String, StockStats> result = new HashMap<>();
                result.put(stock, new StockStats(min, max, avg));
                return result;
            }));
        }

        // Collect results from futures
        Map<String, StockStats> stockStatistics = new HashMap<>();
        for (Future<Map<String, StockStats>> future : futures) {
            stockStatistics.putAll(future.get()); // Retrieve and merge results
        }

        // Print final stock statistics
        stockStatistics.forEach((stock, stats) -> System.out.println(stock + ": " + stats));

        // Shutdown executor
        executor.shutdown();
    }
}
```

---

### **Why Use `Collections.synchronizedList(new ArrayList<>())`?**
- `ConcurrentHashMap` supports **concurrent writes**, but `ArrayList` **is not thread-safe**.
- **Multiple threads might update the list** at the same time (since we are processing stock prices in parallel).
- `Collections.synchronizedList(...)` **ensures thread safety** when adding prices.


---

### **Why Not Just Use `putIfAbsent`?**
- `computeIfAbsent` is preferred **because it avoids extra lookups**.  
  - With `putIfAbsent`, you'd need to fetch the value **again** to add a price.  
  - `computeIfAbsent` **returns the list immediately**, allowing us to directly call `.add(price)`.

--- 

