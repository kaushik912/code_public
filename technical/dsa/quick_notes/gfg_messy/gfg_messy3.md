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
- queue=[1]
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
- queue=[2,3], currCount=2, nextCount=0, dequeued=[]
    - After poll, dequeued=[2], queue=[3]
    - currCount-- => 1
    - Add its children,
        - queue=[3,4,5]
        - nextCount =2
- queue=[3,4,5],currCount=1, nextCount=2,dequeued=[2]
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


# Mirror Tree
Given the root of a binary tree, convert the binary tree to its Mirror tree.

Input: root = [1, 2, 3, N, N, 4]
Output: [1, 3, 2, N, 4]

- We simply swap the left and right node at each node recursively.

void mirror(Node root){

    if(root!=null){
        Node temp = root.left;
        root.left = root.right;
        root.right = temp;
        mirror(root.left);
        mirror(root.right);
    }

}

# Spiral or ZigZag Traversal
Given a root binary tree and the task is to find the spiral order traversal of the tree and return the list containing the elements.
Spiral Order Traversal mean: Starting from level 0 for root node, for all the even levels we print the node's value from right to left and for all the odd levels we print the node's value from left to right.

Input: root = [10, 20, 30, 40, 60]
Output: [10, 20, 30, 60, 40]

## Working Example using plain BFS
- we could do a level-order traversal like before and capture the element in arrays
- result : [[10],[20,30],[40,60]]
- now reverse the even indexed arrays in this result( so that its right to left)
- [[10],[20,30],[60,40]]
- flat-map it to a single result: [10,20,30,60,40]

## Using Two Stacks (pending)



# Connect Nodes
Given the root of a binary tree, connect all nodes at the same level using an additional nextRight pointer for each node. Initially, all nextRight pointers contain garbage values (or null). Your function should set each node’s nextRight pointer to point to its immediate neighbor on the same level. The driver code will print the level-order traversal .

Input: root = [1, 2, 3, 4, 5, N, 6]
Output: [1, #, 2, 3, #, 4, 5, 6, #]

## Working Example using plain BFS
- Use the same approach as before:
- [[n1],[n2,n3],[n4,n5,n6]], where n1 is node with value1, n2 is node with value2 and so on.
- [[n1->null],[n2->n3->null],[n4->n5->n6->null]]
- we need to set the nextRight pointer within these lists as shown above.

## Working Example using Prev Pointer
- While doing a BFS, maintain a prev pointer.
- Lets say we are at level 2, nodes are:
    - [2,3]
    - prev=null
    - Now , we poll 2 (and add its children [4,5] into the queue)
    - prev = 2
    - we poll 3 (and add its children[6] into the queue)
    - prev.nextRight=3
    - prev = 3
        - since every node's nextRight may contain garbage values,
        - when we finish that level, prev would be pointing to last node in that level.
        - we will explicitly set prev.nextRight = null
    - Now it would be [4,5,6] in sub-sequent level
    - prev=null
    - we poll 4 
    - prev = 4
    - we poll 5 
    - prev.nextRight = 5
    - prev = 5
    - poll 6 
    - prev.nextRight = 6
    - prev=6
    - post that level, prev.nextRight=null

- In simple terms, below is the main flow for prev-logic.
```
Node prev=null;
while(!q.isEmpty()){
    Node curr = q.poll();
    if(prev!=null){
        prev.nextRight = curr;
    }
    prev=curr;
}
prev.nextRight=null;
```

## Without using a queue (pending, need more analysis)


# LCA of two nodes in a binary tree
Given the root of a binary tree with all unique values and two nodes value, n1 and n2. Your task is to find the lowest common ancestor of the given two nodes. Both node values are always present in the Binary Tree.

Note: LCA is the first common ancestor of both the nodes n1 and n2 from bottom of tree.

## Working Example

### Example1
           11
         /    \
       22      33
      /  \    /  \
    44   55  66   77

- lets say n1=22, n2=77
- we start from root=11
- we look for n1 or n2 in left subtree
    - we find 22! 
    - we return 22 as the left match
- Now, we look in the right subtree
    - we see 33 ( neither 22 or 77)
    - we look into left and right subtree
        - left : 66 (leaf), is neither 22 or 77. So left subtree is eventually null.
        - right: 77, found a match!, we return right = 77
        - We basically "bubble" up this result
        - 33's left=null and right=77, so it returns 77.
    - So 11's right-subtree has match = 77
- We have 11's left subtree has match=22, right-subtree has match=77
- So 11 is the lca

### Example2
           11
         /    \
       22      33
      /  \
    44   55
         /
       99
- we have say, n1=55 and n2=99
- we start from root=11
- we look into left subtree
    - we find 22 (neither n1 or n2)
        - we further look to the left
            - 44 (left), neither n1 or n2
            - so left=null
        - we now look to right 
            - 55 , it matches n1!
            - Do we stop recursing now?
            - Surprisingly yes!
            - If lets say 99 indeed was a child of 55(which is true in this case), then 55 itself is the correct LCA!
    - So now 22's left=null, right =55, so 22 would return 55. It will bubble up!
- 11's left is 55, right is null
    - so 55 is the lca.

### Key takeways
- once we see n1 or n2, we immediately return
- that returned node bubbles "upward"
- this takes of n1 being ancestor of n2 case or say n1 being root itself.
- Observe the following: 
```
if(root.val==n1 || root.val==n2){
    return root;
}
```
 - If node matches one of the n1 or n2, that node itself is possibly a lca. Why?
    - if the other node is below it, then this node itself is LCA
    - if the other node is elsewhere, then higher levels will handle it via bubbling up.
- Another observation, this is key definition of lca,
```
Node left = lca(root.left,n1,n2);
Node right = lca(root.right,n1,n2);
if(left!=null && right!=null){
    return root;
}
```
- Case of bubbling up:
```
return left!=null ? left : right
```

# Min distance between nodes of a binary tree
Given a binary tree with n nodes and two node values, a and b, your task is to find the minimum distance between them. The given two nodes are guaranteed to be in the binary tree and all node values are unique.

Tree = [11, 22, 33, 44, 55, 66, 77]
a = 77, b = 22
Output: 3

## Approach 1, Root to each node
- from root, find out the path to each node
- then calculate the common path 

path to 77 is [11,33,77]
path to 22 is [11,22]
so combined path from 22 to 77 will be [ 22,11,33,77] = 3
This approach uses auxillary arrays.

## Approach 2, use LCA
- calculate LCA for both nodes
- calculate distance from lca to a, lca to b.
- Sum the distances


