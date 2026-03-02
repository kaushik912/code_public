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
### Stock Buy and Sell Infinite times
```
Given an array arr[] denoting the cost of stock on each day, the task is to find the maximum total profit if we can buy and sell the stocks any number of times.

Note: We can only sell a stock which we have bought earlier and we cannot hold multiple stocks on any day.
Input: arr[] = [100, 180, 260, 310, 40, 535, 695]
Output: 865
```
```
Hint1: AS long as next value is > previous, keep booking profit!
= [180-100]+[260-180]+[310-260]+[695-40] // approach 1
= [310-100] + [695-40] // approach 2
As you can see there are two approaches.

Hint2: Implement approach1
int profit=0;
for(int i=1;i<N;i++){
    if(arr[i]>arr[i-1]){
        profit+=(arr[i]-arr[i-1]);
    }
}
return profit;

Hint3: Approach2
whenever arr[i]< arr[i-1], 
    Other words, if there is a "drop" after a peak, book profit
    reset start to arr[i]

initially,
start=arr[0];
profit=0;
for(int i=1;i<N;i++){
    if(arr[i]<arr[i-1]){
        profit+=(arr[i-1]-start);
        start=arr[i];
    }
}

Hint4: Will this work for edge cases when there is no drop after a peak?
eg: [100, 180, 260, 310, 40, 535, 695],
start=40 at some point,
its an increasing sequence and so arr[i] > arr[i-1],
So we forgot to book profit for this case.
so, handle this case as well:
profit+=(arr[N-1]-start);

Hint6: Add a safe guard in case the entire sequence is decreasing!
profit+=Math.max(arr[N-1]-start,0);

Hint5: Final implementation

start=arr[0];
profit=0;
for(int i=1;i<N;i++){
    if(arr[i]<arr[i-1]){
        profit+=(arr[i-1]-start);
        start=arr[i];
    }
}
profit+=Math.max(arr[N-1]-start,0);

This approach uses fewer transactions than previous one to achieve same result.
But I admit approach1 is simple and straight-forward.

```
### Buy and Sell Stock - Txn Only once
```
You are given an array prices where prices[i] is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

Input: prices = [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
Note that buying on day 2 and selling on day 1 is not allowed because you must buy before you sell.

```
```
Hint1: Max Profit is achieved by "maxDiff".
maxDiff = arr[i]-minSoFar;

Assume 
minSoFar=arr[0];
maxDiff=0;

// iterate from 1 till N
if(arr[i]>=minSoFar){
    maxDiff = Math.max(maxDiff, arr[i]-minSoFar);
}
else{
    minSoFar=arr[i];
}

Hint2: Implement the above idea!

int minSoFar=arr[0];
int maxDiff = 0;
for(int i=1;i<N;i++){
    if(arr[i]>=minSoFar){
        maxDiff = Math.max(maxDiff, arr[i]-minSoFar);
    }
    else{
        minSoFar=arr[i];
    }
}
return maxDiff; //profit

Hint3: If you observe in all the buy and sell stock problems, we usually initialize for 0th index and run logic from 1 till N.

```
# Who has the majority?
```
Given an array arr[] and two elements x and y, return the element that occurs more frequently. If both elements have the same frequency, return the smaller one.

Input: arr[] = [1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 5], x = 4, y = 5
Output: 4
Explanation: frequency of 4 is 4.frequency of 5 is 1.Since 4>1 so return 4
```
```
Hint1:
Simply find out the count of x and y. O(n) pass for each.
in case of tie, return the smaller of x and y.
This is basic. So I won't be writing code.
```

# Frequencies in limited array
```
You are given an array arr[] containing positive integers. The elements in the array arr[] range from  1 to n (where n is the size of the array), and some numbers may be repeated or absent. Your have to count the frequency of all numbers in the range 1 to n and return an array of size n such that result[i] represents the frequency of the number i (1-based indexing).

Input: arr[] = [2, 3, 2, 3, 5]
Output: [0, 2, 2, 0, 1]
Explanation: We have: 1 occurring 0 times, 2 occurring 2 times, 3 occurring 2 times, 4 occurring 0 times, and 5 occurring 1 time.

Time Complexity: O(n)
Auxiliary Space: O(1)
```
```
Hint1: With extra space, we could create a freqcount of numbers.
{2:2, 3:2,5:1}
Now its about populating the result array based on freqcount.

Hint2: Without extra space, lets say we update by the index that corresponding value.
so, output[arr[i]]++
But output array is also of same size as input.
So output[5] would cause index out of bounds exceptions.

So, we need to restrain the values from 0 to N-1
So, if its a 2, we'll store in 1st index
if its a 5, we'll store it in 4th index.
So, for arr[i], output[arr[i]-1]++

Hint3: Implement the solution
int[] output = new int[arr.length];
for(int i=0;i<arr.length;i++){
    output[arr[i]-1]++;
}

Hint4: Another ambitious idea is to use n as a multiplier.
eg: [2, 3, 2, 3, 5]

now, when I see a arr[i], i append n to it in the same array.
so, arr[(arr[i]%n)] +=n
arr[i]%n will ensure it'll always lie between 0 to n-1. (array wise safe)

So, 2 will translate to 3+n, and eventually 3+2n. (index 1 has 3 initially)
So, 3 will translate to 2+2n (index 2 has 2 initially)

So it'll become: [2,3+2n,2+2n,3,5+n]
Now we simply divide by n the entire array
We get:[0,2,2,0,1]

This is for in-place update.
Basically we append 'n' times for each freq at the particular "positional" index and then do a div to get back the freq counts.

```
