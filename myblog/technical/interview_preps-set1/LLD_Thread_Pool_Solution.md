### Thread Pool Solution

---

```java
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

// Task Interface
interface Task {
    void execute();
}

// Worker Thread (Consumer)
class Worker extends Thread {
    private final BlockingQueue<Task> taskQueue;
    private volatile boolean isRunning = true;

    public Worker(BlockingQueue<Task> queue) {
        this.taskQueue = queue;
    }

    @Override
    public void run() {
        while (isRunning) {
            try {
                Task task = taskQueue.take(); // Fetch task
                task.execute(); // Execute task
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public void shutdown() {
        isRunning = false;
        this.interrupt(); // Wake up thread if it's waiting
    }
}

// ThreadPool (Singleton)
class ThreadPool {
    private static ThreadPool instance;
    private final BlockingQueue<Task> taskQueue;
    private final Worker[] workers;

    private ThreadPool(int size) {
        taskQueue = new LinkedBlockingQueue<>();
        workers = new Worker[size];

        // Initialize worker threads
        for (int i = 0; i < size; i++) {
            workers[i] = new Worker(taskQueue);
            workers[i].start();
        }
    }

    public static ThreadPool getInstance(int size) {
        if (instance == null) {
            synchronized (ThreadPool.class) {
                if (instance == null) {
                    instance = new ThreadPool(size);
                }
            }
        }
        return instance;
    }

    public void submit(Task task) {
        try {
            taskQueue.put(task);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void shutdown() {
        for (Worker worker : workers) {
            worker.shutdown();
        }
    }
}

// Main class to test the ThreadPool
public class ThreadPoolTest {
    public static void main(String[] args) {
        ThreadPool pool = ThreadPool.getInstance(3);

        // Submitting sample tasks
        for (int i = 0; i < 10; i++) {
            final int taskId = i;
            pool.submit(() -> System.out.println("Executing Task " + taskId + " by " + Thread.currentThread().getName()));
        }

        // Shutdown the pool after some time
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        pool.shutdown();
    }
}
```

---

### **Key Concepts in This Design:**  
✅ **Singleton Pattern:** Ensures only one instance of `ThreadPool`.  
✅ **Factory Pattern:** Worker threads are created in the constructor.  
✅ **Producer-Consumer Pattern:** Workers consume tasks from a queue.  
✅ **Thread Safety:** `BlockingQueue` ensures safe task execution.  

---

### **Next Steps for You:**  
- Implement **dynamic resizing** to add/remove worker threads at runtime.  
- Introduce **task scheduling strategies** (e.g., priority-based execution).  
- Add **logging and monitoring** to track thread utilization.  
