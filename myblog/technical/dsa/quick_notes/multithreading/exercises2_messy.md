### The Distributed System Boot-Up
```
Problem Statement:
Create a MainServer thread and three Service threads.
Each Service thread takes a random amount of time (1–4 seconds) to initialize.
The MainServer must block and wait until all three services are ready.
As soon as the last service finishes, the MainServer should print: "All services up. Server is now LIVE."
Constraint: You cannot use join(). You must use a CountDownLatch.
```
```
Hint1: Initialize CountDownLatch to 3.
CountDownLatch c = new CountDownLatch(3);

Whenever a service thread finishes task, it will call 
c.countDown()

Hint2: Main server should wait until all services are up
We could use 
c.await(); // it'll wait till the countdown is zero. its a blocking call.

Hint3: Implement 

public class DisBootUp{
    public static void main(String[] args) throws InterruptedException {
		CountDownLatch c = new CountDownLatch(3);
		Thread db = new Thread(new Service(c, "db"));
		Thread cache = new Thread(new Service(c, "cache"));
		Thread messageQ = new Thread(new Service(c, "messageQ"));

		db.start();
		cache.start();
		messageQ.start();
		c.await();// with try-catch or throws
        System.out.println(""All services up. Server is now LIVE.");
	}
}

class Service implements Runnable{
    private CountDownLatch c;
    private String serviceName;
    
    public Service(String serviceName, CountDownLatch c){
        this.serviceName=serviceName;
        this.c=c;
    }

    public void run(){
        System.out.println("Service:"+serviceName+"starting...");
        Thread.sleep((long)(Math.random()*100)); //with try-catch
        c.countDown(); 
        System.out.println("Service:"+serviceName+"started.");
    }   
}

Hint4: Add c.countDown() in a finally block so that it always executes. Otherwise lets say some NPE or exception occured, then the main thread will keep waiting forever!

 public void run(){
    try{
         System.out.println("Service:"+serviceName+"starting...");
         Thread.sleep((long)(Math.random()*100));
         System.out.println("Service:"+serviceName+"started.");
    }catch(InterruptedException e){
        //log exception
    }finally{
        c.countDown(); 
    }        
}

Hint5: Can we reuse our CountDownLatch by resetting to 3 again?
No, we cannot re-use countdown latch. For that, we can use CyclicBarrier.
```
### Multi-stage map-reduce
```
You have 4 Worker Threads. To ensure data integrity, no worker can move to the next round until all 4 workers have finished the current round.

Round 1 (Read): Each worker reads a chunk of data (simulated by a 1–3s sleep).

Round 2 (Process): Each worker performs a calculation (simulated by a 1–3s sleep).

Round 3 (Write): Each worker saves the result (simulated by a 1–3s sleep).

Your Task:

Create a system where all 4 workers must hit a "barrier" after each round.

Once the last worker hits the barrier, a "Barrier Action" (a special task) should run to print: --- Round [X] Complete. Moving to next stage ---.

The workers then automatically proceed to the next round together.
```

```
Hint1: This is classic example of using Cyclic Barrier.
It takes two arguments, 
1. The number of parties: 4 in this case
2. an optional Runnable (Barrier Action): this runs once per round when the barrier is tripped.

Hint2: Unlike latch which has countDown() and await() as separate steps, Barrier uses a single method await().
When a thread calls await(), it stops.
When the last thread calls await(), the barrier "trips", the Barrier Action runs and all threads are released simultaneously.

Hint3: How do we reset the CyclicBarrier for next round?
No need, we can run a for-loop from 1 to 3 for each of the stages.
CyclicBarrier automatically resets after each round.

Hint4: Implement these ideas now!

public class MapReducer{
    public static void main(String[] args){

        BarrierAction ba = new BarrierAction();
        CyclicBarrier cb = new CyclicBarrier(4,ba); // No. of concurrent threads=4
        
        //We start 4 worker threads
        for(int j=0;j<4;j++){         
            Thread w = new Thread(new Worker(cb,j));
            w.start();
        } 
    }
}

class BarrierAction implements Runnable{
    private String[] stages = new String[]{"read","process","write"};
    int stageCounter=0;

    public void run(){
        System.out.println("--- Round Complete. for "+ stages[stageCounter] + " Moving to next stage ---");
        stageCounter++;
    }
}

class Worker implements Runnable{
    private CyclicBarrier cb;
    private int id;
    private String[] stages = new String[]{"read","process","write"};

    public Worker(CyclicBarrier cb, int id){
        this.cb=cb;
        this.id=id;
    }

    public void run(){
        try{
            for(int i=0;i<stages.length;i++){

                Thread.sleep((long)(Math.random()*4000));
                System.out.println("Worker "+id+" done! for stage:"+stages[i]);
                cb.await(); //This is a Blocking call!
                
                //after read, it stops until all other works have finished "read".
                //after process, it stops again until all other works have finished "process".
                //Similarly for write
                //After all workers finish "read", cb gets reset. All threads are released.
            }
            
        }catch(InterruptedException e){

        }
    }
}

Hint5: What if only 3 threads called cb.await() but cb expected 4 parties? 
In that case, the threads will wait forever and won't be release as cb won't get tripped!
So, in such case, we use Phaser instead of Cyclic Barrier.

```