## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

-  This one is for `GFG` questions in no particular order

## Calculate height of a binary tree, AKA maximum depth of a tree
```
Hint:
int height(root){
    if(root!=null){
        return 1 + Math.max(height(root.left),height(root.right));
    }
    return 0;
}

```
# Check if a binary tree is Balanced
```
Hint1: Think about definition of a balanced tree, where height of left and right subtrees doesn't exceed 1.

Hint2: assume we have a height() function, how will we calculate for every sub-tree?

Hint3: 
boolean isBalanced(root){
    if(root!=null){
        int lh = height(root.left);
        int rh = height(root.right);
        return Math.abs(lh-rh)<=1 && isBalanced(root.left) && isBalanced(root.right);
    }
return true;

}
For a skewed tree, it would degenerate to O(N^2)

Hint4: Can we improve further?
If we know at some stage the subtree is unbalanced( lh-rh> 1), we could propogate that result up without computing further. so in the end, either we could see a -1 (indicating some imbalance) or a positive value (indicating balance).

We can't just use a boolean as we also need heights to propogate up for upward comparisons.

boolean isBalanced(root){
    return checkHeight(root)!=-1;
}

boolean checkHeight(root){
    if(root==null){
        return 0;
    }

    int lh = checkHeight(root.left);
    if(lh==-1){
        return -1; //fail fast!
    }

    int rh = checkHeight(root.right);
    if(rh==-1){
        return -1; //fail fast!
    }

    if(Math.abs(lh-rh)>1) return -1; //propogate the imbalance!

    return 1 + Math.max(lh,rh); // calculate height and propogate it up
}

Note: We are embedding the "height" calculation in this checkHeight.


```
### Count Nodes in a tree
```
Hint1: visiting a node counts as 1 and try to repeat that function on left and right sub-trees

Hint2:
int countNodes(Node root){
    
    if(root!=null){
        return 1 + countNodes(root.left) + countNodes(root.right);
    }

    return 0;
}
```

## Count Leaves
Given a Binary Tree of size n, You have to count leaves in it. For example, there are two leaves in the following tree

```
Hint1: Think about definition of a leaf.
if(node.left==null && node.right==null);

Hint2: Do any traversal
If you hit a leaf, return 1;

Hint3: Stitch above ideas into a formula:
return countLeaves(root.left) + countLeaves(root.right)

Hint4: Implement!

int countLeaves(Node root){
    if(root!=null){
        if(root.left==null && root.right==null){
            //leaf node
            return 1;
        }
        return countLeaves(root.left)+countLeaves(root.right);
    }
    return 0;
}

```
# Given a binary tree, find its minimum depth
Shortest path from root to "nearest" leaf node
```
Hint1: WE could use a min function instead of max(height)?
When you visit a node, consider it as 1. Now you visit the left-subtree and right-subtree.
its the lower of the two subtrees. 
Formula: 1 + Math.min(minDepth(root.left),minDepth(root.right));

Hint2: 
in case of right skewed tree, root.left is always null
Then the formula would return 1 as that's the min.
Whereas the definition is from root to leaf. Root itself is not the leaf here.
So, we need to use a fallback call to progress on other side instead of calculating min for such cases.

Hint3:
public int minDepth(Node root){
    if(root!=null){
        if(root.left!=null && root.right!=null){
            //regular case when its a complete node
            return 1 + Math.min(minDepth(root.left),minDepth(root.right));
        }
        if(root.left==null){
            return 1 + minDepth(root.right);
        }
        if(root.right==null){
            return 1 + minDepth(root.left);
        }
    }
    return 0;
}

```
# Shop in Candy Store

```
In a candy store, there are different types of candies available and prices[i] represent the price of  ith types of candies. You are now provided with an attractive offer.

For every candy you buy from the store, you can get up to k other different candies for free. Find the minimum and maximum amount of money needed to buy all the candies.

Note: In both cases, you must take the maximum number of free candies possible during each purchase.

Input: prices[] = [3, 2, 1, 4], k = 2
Output: [3, 7]
```

```
Hint1:
For minimum amount, you should purchase the lowest price (1). 
For picking k free candies, pick the highest amounts (3,4).
Now i am left with 2. Which i still need to purchase. 
So min amount = 1 + 2 = 3


For maximum amount, you do the reverse.
Pick the costliest candy. (4)
Pick the cheapest k candies (1,2)
Again purchase candy with price 3.
So max amount = 4 + 3 = 7

Hint2:
Sort the input : [1,2,3,4] 
we could use two pointers , left and right
For min, pick from left, start picking k from right, do this until left<=right

Hint3:
int min=0;
int left=0;
right=N-1;
while( left<=right && right>=0 && left<prices.length){
    min+= prices[left++];
    int count=0;
    while(count++<k){
        right--
    }
}

int max=0;
left=0;
right=N-1;
while(left<=right && right>=0 && left<prices.length){
    max+=prices[right--];
    int count=0;
    while(count++<k){
        left++;
    }
}

```

# Page Fault
```
Given a sequence of pages in an array pages[] of length N and memory capacity C, find the number of page faults using Least Recently Used (LRU) Algorithm. 

Input: N = 9, C = 4
pages = {5, 0, 1, 3, 2, 4, 1, 0, 5}
Output: 8
```
```
Hint1:
Have a basic working idea of LRU to solve this problem.

```
```
Hint2: For quick solution if allowed, Use a LinkedHashSet<> to store Key
In LinkedHashSet<>, oldest will be at the front and newest will be towards the end.
It maintains order and it has set for quick lookup operations.

if value exists in Set
    Remove the key in set
    Add this element to set ( newest will be at the end)
if value doesn't exist in set
    we need to either add or replace existing based on set.size and Capacity.
    if set.size()==C
        Remove oldest element (oldest will be in the beginning)
        In Java, beginning element can be accessed using set.iterator().next()
        Add this new element (new at the end)
    otherwise
        Add this new element to set ( new at the end)

Since we use a Set, all operations are O(1)

```
```
Hint2: Implement the above idea!
public int pageFaults(int[] nums, int C){

    LinkedHashSet<Integer> s = new LinkedHashSet<>();
    int pagefault=0;
    for(int num: nums){
        if(s.containsKey(num)){
            s.remove(num);    
        }else{
            pagefault++;
            // if it exceeded capacatiy
            if(s.size()==C){
                Integer first = s.iterator().next();
                s.remove(first);    
            }
        }
        s.add(num);
    }
    return pagefault;

}
```

