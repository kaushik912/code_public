## Implement LRU

```
Hint1: LRU works as follows:
Lets say we add new elements to beginning of a list. So old would be towards the end.

pages: {5,0,1,3,2,1}

First 4 elements would be Like:
{5}
{0,5}
{1,0,5}
{3,1,0,5}

Now comes a 2
Since our capacity is already 4, we need to evict someone to make space for this.

LRU says evict the "least recently used" key. 
So in this case, its 5.
So we remove 5 and insert 2 at the beginning.

if(!list.contains(key)){
    if(list.size()==C){
        list.remove(list.size()-1); // evict last
        list.addFirst(newkey); // O(1)
    }
}

So it becomes : {2,3,1,0}
Now lets move to next element, which is 1

1 is already present in the list, but we need to move it to front.
So, we remove 1 and add 1 to the front.
if(list.contains(key)){
    list.remove(Integer.valueOf(key)); // Deleting a node takes O(n)
    list.addFirst(key); //O(1)
}

```
Hint2:
Implement this idea.

List<Integer> lruSimple = new LinkedList<>();
int C=4;
for(int page: pages){
    if(!lruSimple.contains(page)){ //O(C)
        if(lruSimple.size()==C){
            lruSimple.remove(lruSimple.size()-1); //remove by index
        }
        lruSimple.addFirst(page);
    }else{
        lruSimple.remove(Integer.valueOf(page)); // remove by node, O(C)
        lruSimple.addFirst(page);
    }
}
Time complexity : O(N*C)

```
Hint3: 

So above solution works but its O(C) for search and removal. 

search can be optimized using a map.

If we have a single linked list, removal will take O(n) since we need to iterate to that point and adjust prev and next pointers.

removal can be optimized using a DLL since it has access to prev and next pointer. 
Then we could delete it in O(1).

Map should store reference to the node which can be used later by our DLL to remove.
Map<Integer,Node> map; 

We are leaning towards a Custom DLL + Map.
```

```
Hint4

How do we delete a node in DLL ?

remove(Node n){
    n.prev.next=n.next;
    n.next.prev = n.prev;
}

```
```
Hint5:

For the LRU itself, we will have:
put(int key,value);
get(int key);


Since we are building our own DLL, we need the followig operations:
insertAtFront(Node n);
remove(Node n);

```
Hint6:

public class LRUComplex{
	
	Node head = new Node(0,0); //dummy
    Node tail = new Node(0,0); //dummy
   
    class Node{
        Node prev;
        Node next;
        int val;
        int key;
        Node(int key, int val){
            this.key=key;
            this.val = val;
        }
    }

    public LRUComplex(){
    	
        head.next=tail;
        tail.prev=head;
    }

    Map<Integer,Node> map = new HashMap<>();

    int C=3;

    void put(int key, int value){
        if(!map.containsKey(key)){
            Node n = new Node(key,value);
            if(map.size()==C){
                //evict lru
                Node lru = tail.prev;
                remove(lru);
                map.remove(lru.key);
            }
            insertAtFront(n);
            map.put(key,n);
        }else{
            //move it to front
            Node n = map.get(key);
            n.val=value;
            remove(n);
            insertAtFront(n);       
        }
    }

    public void insertAtFront(Node n){
        Node nextNode = head.next;
        nextNode.prev=n;
        n.next = nextNode;
        head.next=n;
        n.prev=head;
    }

    public void remove(Node n){
        n.prev.next=n.next;
        n.next.prev = n.prev;
    }
    
    public int get(int key) {
    	if(!map.containsKey(key)) return -1;
    	
    	Node n = map.get(key);
    	remove(n);
        insertAtFront(n);
        return n.val;
    	
    }

}

This one has lot of implementation details. 
I need to rewrite a better version.
```

```
Hint7:
You can also use LinkedHashMap which is default implementation of LRU provided in Java.
It has a boolean arg accessOrder=true which will order keys based on access order
You could extend the LinkedHashMap and override the removeEldestEntry() method.

```