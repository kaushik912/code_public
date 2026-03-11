### Print alternate threads
```
T1: 1,3,5...
T2: 2,4,6...
Write a program to print T1,T2 alternately : 1,2,3.. 
```
```
Hint1: use wait() and notify() on a lock.
The lock should be at class level, not individual thread.
Now, we could initialize each thread with some int value to differentiate the two threads.

Take a counter, shared variable. (use an wrapper object and not primitive to pass around)
Pass the lock as well to each of the threads (odd and even counter threads).
if counter is odd, odd thread gets to print.
if counter is even, even thread gets to print.

So, each thread, 
enter a lock, 
    if counter is odd and thread is even (mismatch), then wait()
    otherwise,
        print the counter based on eligibility
        increments the counter
        call notify(), release the lock

Hint2: Implement the above idea

class PrintAlternate{
    private static Object lock = new Object();

    public static void main(String[] args){
        int[] counter = new int[1];

        Thread odd = new Thread(new OddPrinter(1,counter,lock));
        Thread even = new Thread(new EvenPrinter(2,counter,lock));
        odd.start();
        even.start();
    }
    
}

class OddPrinter implements Runnable{
    private int id;
    private int[] counter;
    private Object lock;
    public OddPrinter(int id, int[] counter, Object lock){
        this.id = id;
        this.counter=counter;
        this.lock=lock;
    }

    public void run(){
        while(counter[0]< 20){
            synchronized(lock){
                if(counter[0]%2!=0){
                    System.out.println("Thread:"+id + ", number:"counter[0]);
                    counter[0]++;
                    lock.notify();
                }else{
                    lock.wait();
                }
            }
        }   
    }
}

class EvenPrinter implements Runnable{
    private int id;
    private int[] counter;
    private Object lock;
    public EvenPrinter(int id, int[] counter, Object lock){
        this.id = id;
        this.counter=counter;
        this.lock=lock;
    }

    public void run(){
        while(counter[0]< 20){
            synchronized(lock){
                if(counter[0]%2==0){
                    System.out.println("Thread:"+id + ", number:"counter[0]);
                    counter[0]++;
                    lock.notify();
                }else{
                    lock.wait();
                }
            }
        }   
    }
}

Hint3: This could be further optimized by using a single boolean variable isOddThread, etc.

```
### Print ABCABCABC..
```
Thread A prints A
Thread B prints B
Thread C prints C
Write a program that prints ABCABC..
```
```
Hint1: Extend the previous idea.
Again use a counter shared variable.
if counter%3==0, print A, 
if counter%3==1, print B
if counter%3==2, print C

Hint2:
Now, instead of hardcoding 0,1,2 what if we passed 0,1,2 as ids to each thread and used them during comparison?
That way, we can write a generic code that will work for all three threads.

KEY POINT: You need to use lock.notifyAll() instead of just lock.notify() as we are more than one thread waiting.

Hint3: Sketch out this idea
class Printer implements Runnable{
    private int id;
    private String value;
    private Object lock;
    private int[] counter;

    public Printer(int id, String value, Object lock, int[] counter){
        this.id=id;
        this.value=value;
        this.lock=lock;
        this.counter=counter;
    }

    public void run(){
       while(counter[0]<20) {
    		synchronized(lock){
                
                if(counter[0]%3==id){
                    System.out.println("Thread id:"+ id + " value="+value);
                    counter[0]++;
                    lock.notifyAll();
                }else{
                    try {
    					lock.wait();
    				} catch (InterruptedException e) {
    					// TODO Auto-generated catch block
    					e.printStackTrace();
    				}
                }
            }
    	}
    }
}

public class ThreadPrinter{
    static Object lock = new Object();
    static int[] counter = new int[1];
    public static void main(String[] args){
        Thread a = new Thread(new Printer(0,"A",lock,counter)); //0
        Thread b = new Thread(new Printer(1,"B",lock,counter)); //1
        Thread c = new Thread(new Printer(2,"C",lock,counter)); //2
        // since we do %3, it'll be one of 0,1,2

        a.start();
        b.start();
        c.start();
    }
}

Hint4: Optimize little bit.
Recommended solution using "while" inside synchronized block for the wait() call.
Also, handles the edge case when counter has exceeded max and threads are not notified.

public void run(){
       while(true) {
    		synchronized(lock){

                if(counter[0]>=max){
                    //handle edge case of hung threads when counter has exceeded max
                    lock.notifyAll(); 
                    break; //clean exit of while(true) loop
                }

                while(counter[0]<max && counter[0]!=id){ 
                    //standard wait pattern using while
                     try {
    					lock.wait();
    				} catch (InterruptedException e) {
    					e.printStackTrace();
    				}
                }

                if(counter[0]<max && counter[0]==id){
                    //do the work!
                    System.out.println("Thread id:"+ id + " value="+value);
                    counter[0]++;
                    lock.notifyAll();
                }
            }
    	}
}

```
### Solve producer consumer problem
```
producer produces items and pushes it to a fixed capacity queue.
consumer consumes items from this queue.
if queue has reached the limit, then producer waits till consumer consumes 
if queue has reached zero, consumer will wait till producer puts any data.

To simulate a real life experience, add a delay of random seconds (say 4s) while consuming and producing.
Print "waiting" in both consumer and producer ends as applicable.

```
```
Hint1: Queue is a shared resource.
wait() to be called inside while() based on the condition not met,
Queue<Integer> q = new LinkedList<>();


Hint2: Write Producer and Consumer as separate threads.

class Producer implements Runnable{
    Queue<Integer> q;
    int capacity;
    Object lock;

    public Producer(Queue<Integer> q, int capacity, Object lock){
        this.q=q;
        this.capacity=capacity;
        this.lock=lock;
    }

    public void run(){
        while(true){
            synchronized(lock){
                while(q.size()==capacity){
                        lock.wait();         
                }
                int newValue = (int)(Math.random()*1000); // always wrap computation before cast 
                // because cast has higher precedence than multiplication!

                q.offer(newValue);
                System.out.println("Producer pushed:"+ newValue);
                lock.notify();
            }
            //Keep Sleep outside synchronized block
            Thread.sleep((long) (Math.random() * 4000)); //with try-catch
        }
    }
}

class Consumer implements Runnable{
    Queue<Integer> q;
    int capacity;
    Object lock;

    public Consumer(Queue<Integer> q, int capacity, Object lock){
        this.q=q;
        this.capacity=capacity;
        this.lock=lock;
    }

    public void run(){
        while(true){
            synchronized(lock){
                while(q.size()==0){
                        lock.wait();//with try-catch         
                }
                int polledValue = q.poll();
                System.out.println("Consumer consumed:"+ polledValue);
                lock.notify(); 
            }
            //Keep Sleep outside synchronized block
            Thread.sleep((int)(Math.random()*4000));//with try-catch
        }
    }
}

public class ProdConsumer {
    private static Object lock = new Object();
    private static Queue<Integer> q = new LinkedList<>();

    public static void main(String[] args){
        Thread p = new Thread(new Producer(q,10,lock));
        Thread c = new Thread(new Consumer(q,10,lock));
        p.start();
        c.start();
    }

}

Hint3: Small perf hack
Instead of Math.random, where multiple threads would try to get the "seed" but only one thread will eventually get it, we could instead use ThreadLocalRandom
eg: ThreadLocalRandom.current().nextLong(4001); // gives random between [0,4001)
This is way faster than Math.random()

```

### Producer Consumer using BlockingQueue
```
Solve the same problem but using Java concurrent packages.
```

```
Hint1:
BlockingQueue is an interface.
ArrayBlockingQueue is concrete implementation.
We need to specify a capacity to initialize the queue.

BlockingQueue<Integer> q = new ArrayBlockingQueue<>(10);

Hint2:
understand BlockingQueue operations.
q.put() puts the value into the queue, auto blocks if the queue is full!
q.take() takes value from the queue, auto blocks if queue is empty!

So no need to write the wait() and notify() calls.
So, put() and take() are the key methods.

Hint3: Implement
class Producer implements Runnable{
    BlockingQueue<Integer> q;
    
    public Producer(BlockingQueue<Integer> q){
        this.q=q;
    }

    public void run(){
        while(true){
            int newValue = (int)(Math.random()*1000);
            q.put(newValue);
            System.out.println("value pushed!:"+newValue);
        }
        
        Thread.sleep((int)(Math.random()*4000)); //with try-catch
    }
}

class Consumer implements Runnable{
    BlockingQueue<Integer> q;
    
    public Consumer(BlockingQueue<Integer> q){
        this.q=q;
    }

    public void run(){
        while(true){
            int polledValue = q.take(); //with try-catch for interrupted exception
            System.out.println("value consumed!:"+polledValue);
        }
        
        Thread.sleep((int)(Math.random()*4000)); //with try-catch for interrupted exception
    }
}

public class ProdConsumerBlocking {
	public static void main(String[] args) throws Exception {
		BlockingQueue<Integer> q = new ArrayBlockingQueue<>(10);//initial capacity of 10
		Thread p = new Thread(new Producer(q));
		Thread c = new Thread(new Consumer(q));
		p.start();
		c.start();
	}
}
```

