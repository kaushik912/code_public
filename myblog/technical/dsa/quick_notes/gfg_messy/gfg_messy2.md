## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

-  This one is for `GFG` questions in no particular order

# Balanced Tree
- A binary tree is considered height-balanced if the absolute difference in heights of the left and right subtrees is at most 1 for every node in the tree.
- So we need to find height of a binary tree first.
    - height of a tree is 1 + max ( height(root.left), height(root.right)), provided those nodes exist (otherwise return 0).
    - So , 1 + max of (height of left subtree, height of right subtree)

- So balanced tree at node is ( say is defined by isBalance(node))
    -  balanceCheck= Math.abs( height(node.left) - height(node.right)) <= 1
-  But we need to check this for all nodes, not just root.
    - so its a recursive call.
    -  balanceCheck && isBalance(root.left) && isBalance(root.right)
- Base case: when the node is null, its balanced. so return true.

- There are several calls to height() one via balanceCheck and another via the isBalance recursive call. 
- We are re-computing the height several times, which can be avoided.

### Optimized version
- in the height calculation, we already know height of left and right subtrees.
- we usually use the max for comparing the greater of the subtrees and add 1 to it.
- additionally, we could also check if their heights differ by atmost 1, if not , we can flag it as a "unbalanced" node

- lh (left subtree height)= height(root.left), rh = height(root.right)
- if(|lh-rh| >1), return -1 ( special value indicating that node is unbalanced)
- now , if some lh or rh value turns out to be -1, we propagate the same above.
- So we get either height of a tree or `-1` in case 

- recursion for this modified height function, we can say `heightOrFail()` is setup as follows:
 - first recursively call heightOrFail() on left node.
    - in case of any unbalance nodes, return -1 (early exit)
    - we don't even compute the right subtree.
-  otherwise call heightOrFail() on right node
    - in case of any unbalance case, return -1
- Otherwise if both give positive height, check their difference and verify if they are balanced.
    - isBalanced is just going to check if heightOrFail() returns -1 or not.
    - Calculate height as usual in case its a balanced node.

### Basic idea
- While calculating left and right heights of a given node, also calculate if that node is `balanced` in the calculation.
- in case its unbalanced in either left-subtree or right-subtree, propogate the result of -1 up.

# Count leaves
Given a Binary Tree of size n, You have to count leaves in it. For example, there are two leaves in the following tree

- idea is to define what is a leaf
- a leaf is a node that has no children
- so recursively go down via any traversal method 
- lets say i use post-order, node-left-right
    
    if(node!=null){
        if(node.left==null && node.right==null)
            return 1; //found leaf
        return count(node.left)+count(node.right);
    }
    return 0;

### Basic Idea
    - correctly define the leaf node
    - use any regular traversal technique to traverse the nodes

# Given a binary tree, find its minimum depth.
- calculate distance from root to each leaf node.
- whichever is minimum, that is the minimum depth.
    
- Using recursion,
- assume min is an array object with initial value Integer.MAX_VALUE
- min = int[1], min[0]= Integer.MAX_VALUE

void minDepth(node, len, min){
    if(node!=null){
            if(node.left==null && node.right==null){
                //leaf node
                //update min
                min[0] = Math.min(min[0],len);
                return ;
            }
            minDepth(node.left, len+1,min);
            minDepth(node.right,len+1,min);
    }
}

int minDepth(root){
    // invoke function
    //initial len is 1 as we are counting nodes and we are already at root
    minDepth(root,len=1,min);
    return min[0];
}

### Basic Idea
- Use a len to update length of each node-path seen so far when you traverse down the tree.
- once you hit the leaf, update the min by comparing the len so far.
- Optional: You can do extra pruning using : `if (len >= min[0]) return;` since there is no point looking into those paths.


# Shop in Candy Store
In a candy store, there are different types of candies available and prices[i] represent the price of  ith types of candies. You are now provided with an attractive offer.

For every candy you buy from the store, you can get up to k other different candies for free. Find the minimum and maximum amount of money needed to buy all the candies.

Note: In both cases, you must take the maximum number of free candies possible during each purchase.

Input: prices[] = [3, 2, 1, 4], k = 2
Output: [3, 7]

### Minimum Amount
- we sort the array
- [1,2,3,4]
- for minimum amount, pick 1, k=2, i will pick 3 and 4 for free to save money.
- remaining left is 2.
- 1 + 2 = 3
- More formally, lets keep two indices, left and right
    - pick an item from left, prices[left], left++
    - pick k items from right for free, right -=k
    - do until left <= right

### For Maximum amount
- we do the reverse
- we pick from right , most expensive item, right--
- for each item picked, left +=k, pick k free items
- do this while left<=right
- optionally: you could do a tigher check while picking free items : if ( left<=right) { //only then pick free items}, this is just for our ease of understanding.

### Key points
- Use the two pointer approach
- For minimum amount, we pick the lowest amount and pick k "costliest" items for free.
- For maximum amount, we pick the highest amount and pick k "cheapest" items for free.


# Page Fault
Given a sequence of pages in an array pages[] of length N and memory capacity C, find the number of page faults using Least Recently Used (LRU) Algorithm. 

Input: N = 9, C = 4
pages = {5, 0, 1, 3, 2, 4, 1, 0, 5}
Output: 8

- initially each page requested would result in page-fault.
- {3,1,0,5}, pagefault=4
- comes 2, replaces 5, {2,3,1,0}, pagefault=5
- comes 4, replaces 0, {4,2,3,1}, pagefault=6
- comes 1, its already present, { 1,4,2,3}, pagefault=6+0
- comes 0, replaces 3, {0,1,4,2}, pagefault=7
- comes 5, replaces 2, {5,0,1,4}, pagefault=8

- To solve this problem, we need to use a map and a doubly-linked list
- whenever a page request comes, 
    - if not present in map, 
        - pagefault++
        - if map.size() == capacity
            - remove that DLL tail key in map
            - remove tail from DLL
        - insert new page key in map
        - insert new page in front for DLL
    - else //its present in map
        - fetch node from map
        - remove node from current position in DLL 
        - re-insert node in front for DLL
- We use a Map that stores <key,Node> information. 
- Java's LinkedList has O(n) for removing a node. So we need to implement custom DLL.
- LinkedList implements several interfaces: List, Deque, and Queue.
- Some useful linked list operations: addFirst(),addLast(),removeFirst(), removeLast(),remove(Object)
- list.add(index, value); // inserts node at particular index, 
- list.set(index, value); // replaces node at particular index with new value


# Max subarray sum
You are given an integer array arr[]. You need to find the maximum sum of a subarray (containing at least one element) in the array arr[].
Input: arr[] = [2, 3, -8, 7, -1, 2, 3]
Output: 11
- calculate running sum 
- If the running sum ever becomes below 0, reset the runningSum to 0.
- If running sum is increasing, update the maxSum. 

### Working Example
- Comes 2 , RS=2, MS=2
- Comes 3, RS=5, MS = 5
- Comes -8, RS=-3=>0, MS = 5 (remains old good sum)
- Comes 7, RS=7, MS = 7 (updated!)
- Comes -1, RS=6, MS= 7
- Comes 2, RS = 8, MS=8
- Comes 3, RS=11, MS=11

- Special case: If all numbers are negative, we need to handle separately in the beginning itself. 
    - eg: [-5,-2,-3], then maximum sum of subarray is max in that array: -2

    

