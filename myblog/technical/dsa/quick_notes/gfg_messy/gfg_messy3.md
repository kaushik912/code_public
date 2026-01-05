## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

-  This one is for `GFG` questions in no particular order

# Level Order Traversal
Given root of a binary Tree,  return its level order traversal.
Input: root = [1, 2, 3, 4, 5, 6, 7, N, N, N, N, N, 8]
Output: [[1], [2, 3], [4, 5, 6, 7], [8]]

## Working Example
- Assume queue = [1]

- de-queue whatever is present in queue and enqueue the children.
- queue: [1]
    - dequeued: [1], queue:[2,3], result = [..[dequeued]] = [[1]]
- queue:[2,3]
  - dequeued: [2,3], queue:[4,5,6,7], result = [..[dequeued]] = [[1][2,3]]
- queue:[4,5,6,7]
  - dequeued: [4,5,6,7], queue:[8], result = [..[dequeued]] = [[1][2,3][4,5,6,7]]
- queue:[8]
  - dequeued: [8], queue:[], result = [..[dequeued]] = [[1][2,3][4,5,6,7][8]]


### Core idea
 - At the beginning of each iteration, We first de-queue all existing elements in queue (current level) and collect that to resultList. This "clears" that level.
 - For each de-queued element, we enqueue their children to the queue. 
    - These next-level items become available in next iteration for de-queuing. 
 - Using this way, we achieve the BFS.
 
 ## Java Points
 - Queue is implemented by a LinkedList in Java.
 - to add to a queue, we use queue.offer() in Java
 - to de-queue , we use queue.poll() in Java
 - queue.size() is O(1) in Java as queue/LL internally maintains its size.


## Working Example using two count approoach
- Assume queue = [1], 

- dequeued=[], result=[], currCount=1, nextCount=0
- poll the queue 
    - since we polled, decrement the currCount
    - add the polled element to dequeued.
    - enqueue its children.
        - for each child enqueued, increment nextCount
    - if currCount reaches 0
        - result.add(runList)
        - dequeued=[]
        - currCount = nextCount
        - nextCount = 0

queue=[1]
    - After poll, dequeued=[1], queue=[]
    - currCount-- => 0
    - Add its children,
        - queue=[2,3]
        - nextCount =2
    - since currCount =0
        - result = [[1]]
        - currCount =2
        - nextCount=0
        - dequeued=[]
    
queue=[2,3], currCount=2, nextCount=0, dequeued=[]
    - After poll, dequeued=[2], queue=[3]
    - currCount-- => 1
    - Add its children,
        - queue=[3,4,5]
        - nextCount =2

queue=[3,4,5],currCount=1, nextCount=2,dequeued=[2]
    - After poll, dequeued=[2,3], queue=[4,5]
    - currCount-- => 0
    - Add its children,
        - queue=[4,5,6,7]
        - nextCount =4
    - since currCount =0
        - result = [[1],[2,3]]
        - currCount =4
        - nextCount=0
        - dequeued=[] 

and so on..

### Key Idea in two count
- currCount maintains nodes at current level
- nextCount maintains nodes at next level
- when currCount reaches 0, then its time to update it to nextCount and reset nextCount.
    - Its like that particular level nodes are finished
    - Its time to collect that nodes collected so far (dequeued[]) into the level-order list (result[]).
    - We then reset the (dequeued[]) list.

### Useful for left-view and right-views    
- This idea may be useful in case we wish to print right-view of a tree. whenever the currCount==1(last element at that level), we could store it in a separate result.
- For left-view, whenever we do the count reset, we could set a boolean flag atLevelBeginning=true
    - When this is true, that element is first element in that level. 
    - Reset this flag after adding that element to your result.
- Of course, the previous approach may also work fine if we can check the iteration number while popping existing elements from queue.

