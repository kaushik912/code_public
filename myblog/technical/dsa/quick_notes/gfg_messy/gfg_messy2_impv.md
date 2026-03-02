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

# Max subarray sum

```
You are given an integer array arr[]. You need to find the maximum sum of a subarray (containing at least one element) in the array arr[].
Input: arr[] = [2, 3, -8, 7, -1, 2, 3]
Output: 11
```
```
Hint1: The way you accumulate runningSum matters.

Hint2:  If we add arr[i] to our runningSum in beginning,
if runningSum < 0, we need to reset runningSum to 0.
if runningSum > 0, then we are good as its an increasing sequence , so we need to update max.

Hint3: Lets implement this solution
int maxSum=0;
int runningSum=0;
for(i=0;i<n;i++){
    runningSum+=arr[i];
    if(runningSum<0){
        runningSum=0;
    }else{
        maxSum = Math.max(maxSum, runningSum);
    }
}

Hint4: The above solution breaks when all numbers are negative.
Because runningSum is always reset to 0 and so the maxSum would also be 0.
But we need to calculate max of all the negative numbers.
One approach is to use a separate loop to handle this.

Hint5: We could also make this solution generic.
But we need to tweak our approach of runningSum little bit.

Instead of first accumulating arr[i] into runningSum, 
check existing runningSum first ( accumulated from previous iteration) and decide whether to add current element or not.

Hint6: So, we need to first define previous currentSum and maxSum before we start checking.
So, initially lets say,
currSum = arr[0]
maxSum = arr[0]

for(int i=1;i<n;i++){
    if(currSum>0){
        currSum+=arr[i]; //accumulate 
    }else{
        currSum=arr[i]; //reset: discard old and startover at i
    }
    maxSum = Math.max(currSum,maxSum);
}

Here, if all numbers are negative, it'll essentially "max" all the negatives and provide the answer. 

If numbers are both positive and negative, 

when currSum>0, we simply add our current arr[i].
when currSum < 0, we reset it to the current element ( and not 0).

So, if our array was [-7,12]
currSum =-7 < 0 , so we reset currSum to 12

Now we update maxSum based on the updated currSum (either it had accumulated or reset )

I would say both approaches are fine. Its important to know the special cases.

Hint7: What if they also want the indices where the max sum lies?
We need to do additional book keeping.
Lets assume, we have three variables:
start=0; // pointing to first element
end = 0; //pointing to first element
tempStart=0; // also pointing to first element.

Whenever we reset, we need to update tempStart=i ( note down the new beginning)
Whenever we our currSum>maxSum, we need to update
    maxSum=currSum
    start=tempStart ( we already marked this in reset)
    end=i ( the place where we hit maximum)

So, our max sub-array would lie in [start,end]

int start=0;
int end=0;
int tempStart=0;
int maxSum=arr[0];
int currSum=arr[0];
for(int i=1;i<N;i++){
    if(currSum > 0){
        currSum+=arr[i];
    }else{
        currSum=arr[i];
        tempStart=i;
    }
    if(currSum > maxSum){
        maxSum = currSum;
        start=tempStart;
        end = i;
    }
}


```
### Stock Buy and Sell
```
Given an array arr[] denoting the cost of stock on each day, the task is to find the maximum total profit if we can buy and sell the stocks any number of times.

Note: We can only sell a stock which we have bought earlier and we cannot hold multiple stocks on any day.
Input: arr[] = [100, 180, 260, 310, 40, 535, 695]
Output: 865
```
```
Hint1: 

```

