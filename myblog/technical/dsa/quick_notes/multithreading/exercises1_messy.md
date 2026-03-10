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
### Print ABC 
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