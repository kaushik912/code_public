### Problem 
I have to process 1000 stock prices from a text file.  Each line in text contains a stock name, price.
How can i use futures to calculate average, min and max price per stock?

To process **1,000 stock prices** from a text file and calculate **average, min, and max price per stock**, we can use **Java's `ExecutorService` and `Future`** for parallel computation.

---

### **How This Works**
1. **Reads `stocks.txt`** where each line is:  
   ```
   AAPL,150.50
   AAPL,152.00
   TSLA,700.25
   TSLA,698.75
   ```
2. **Stores stock prices** in a `ConcurrentHashMap<String, List<Double>>`.
3. **Submits tasks to a thread pool**, where each task:
   - Finds **min, max, and average** price for a stock.
   - Returns the result in a `Future<Map<String, StockStats>>`.
4. **Retrieves results from `Future`**, merges them, and prints stock statistics.
5. **Shuts down the thread pool**.

---
