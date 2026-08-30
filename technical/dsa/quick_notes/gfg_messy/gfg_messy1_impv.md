## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

-  This one is for `GFG` questions in no particular order

# Problem: Replace all 0's with 5

```
You are given an integer n. You need to convert all zeroes of n to 5.
Input: n = 1004
Output: 1554
```

```
Hint1: Use mod and div operations
- 1004 %10 = 4, 1004/10 = 100, k=0
- 100 %10 =0, 100/10 = 10, k=1
- 10%10 =0, 10/10 = 1, k=2
- 1%10 = 1, 1/1 = 0, k=3

Hint2: 
what if you see a 0 at some position k, how would you replace it with 5?

in the decimal system, the value at position k is (10^k)*(place-value)
Some examples,
at k=0, (10^0)*(4)
at k=1, (10^1)*(0)

Hint3:
Combine above two ideas to do the replacement

Hint4: 
int k=0;
int res=0;
while(n!=0){
    int rem = n%10;
    if(rem==0){
        res+=Math.pow(10,k++)*5;
    }else{
        res+=Math.pow(10,k++)*rem;
    }
    n = n/10; 
}

Hint5:
Ask the interview if you can convert number to a string. If yes, then it can be done with character replacement.
```
# find equilibrium point in an array
```
Given an array of integers arr[], the task is to find the first equilibrium point in the array.

The equilibrium point in an array is an index (0-based indexing) such that the sum of all elements before that index is the same as the sum of elements after it. Return -1 if no such point exists. 

Input: arr[] = [1, 2, 0, 3]
```

```
Hint1: Try more examples!
What if my array is [1, 2, 5, 3], equilibrium index is still 2

Hint2: if you are at index i, can you access sum upto (i-1) i.e. leftSum?
- Think updating **later** in loop and accessing that sum first in next iteration

Hint3: How would you calculate rightSum?
Suppose you had total sum , eg: [1, 2, 5, 3], sum = 11
Now if you are at index 2, leftSum = 3, rightSum = 11-3-5
so rightSum = sum -leftSum-arr[i]

Hint4: Use above ideas to solve!
int leftSum=0; //before i=0, there is no left element!

int sum=0;
for(int num:arr){
    sum+=num;
}

for(int i=0;i<arr.length;i++){
    int rightSum = sum - leftSum-arr[i];
    if(leftSum==rightSum){
        return i; // found the answer!
    }
    leftSum+=arr[i]; // update later
}
return -1; // in case of no answer
```

# Find third largest element 
```
Given an array, arr of positive integers. 
Find the third largest element in it. Return -1 if the third largest element is not found.
Expected Time Complexity: O(n)
Expected Space Complexity: O(1)

Input: arr[] = [2, 4, 1, 3, 5]
Output: 3
```
```
Hint1: Ask if the numbers are distinct. This will matter the logic.

Hint2: Assume you know max, how would you calculate secondMax?
- Same max calculation but additionally it should be strictly less than max
- ThirdMax: same max calculation but it should be strictly less than secondMax

Hint3: You see a pattern, so generalize the above idea, 

int nextMax(int[] nums, int currMax){
    int nextMax=Integer.MIN_VALUE;
    for(int num : nums){
        if(num < currMax){
            if(num > nextMax){
                nextMax = num; // this updates nextMax to highest value < currMax
            }
        }
    }
    return nextMax;
}

int secondMax = nextMax(nums,max);
int thirdMax = nextMax(nums,secondMax); // use error handling etc.

```
```
Approach2
- The previous approach is fine as its efficient. 
- This approach uses trickle-down logic.
- Assume we have m1,m2 and m3 for the three highest max values. 
- if arr[i]> m1
    m3 = m2
    m2 = m1
    m1 = arr[i]
- if arr[i]< m1 && arr[i] > m2
    m3 = m2
    m2 = arr[i]
- if arr[i] < m2 && arr[i] > m3
    m3 = arr[i]
      
```
```
Approach 3
- To find top-K, then you could use a min heap.
- Since we want distinct max values, we can use a set to track duplicates
- How can min-heap help in top-k? It sounds counter-intuitive.
- That's because of the way we add elements to the min-heap
- If you get a value larger than heap's root, we replace root with element
- Since heap is bound by K, we end up keeping top K elements (displacing smaller elements with larger elements, max-K "survive" in that heap).
- So space complexity is O(K) since we keep only k elements in heap, time complexity would be N*Log(K). Each heap operation takes Log(K) and we are processing N elements, so its N*Log(K)
- So inserting into a min-heap uses "survival of fittest" strategy as it removes weaker keys so that only larger keys remain.
```

# Max and SecondMax
```
Given an array arr[] of positive integers which may have duplicates. The task is to find the maximum and second maximum from the array, and both of them should be different from each other, and If no second maximum exists, then the second maximum will be -1.

Input: arr[] = [2, 1, 2]
Output: [2, 1]

Input: arr[] = [3, 3, 3]
Output: [3, -1]
```
```
This is similar to previous problem. So it can be solved easily using the modified max approach or the tickle-down approach with m1,m2 variables.
Good for practice!
```

# Min distance in array

```
You are given an array, arr[]. Find the minimum index based distance between two distinct elements of the array, x and y. Return -1, if either x or y does not exist in the array.

Input: arr[] = [1, 2, 3, 2, 1 ], x = 1, y = 2
Output: 1

Explanation: x = 1 and y = 2. 
There are two distances between x and y, which are 1 and 3 out of which the least is 1.
```
```
hint1: keep track of lastSeenIndex whenever you encounter a x or y

hint2: when you see the "other" number, calculate distance to previous one and update your minDist.

hint3: say arr[i]==x or arr[i]==y, and you also have lastSeenIndex, how do you find if its a x,y pair?
arr[i]!=arr[lastSeenIndex] indicates a pair!, // provided lastSeenIndex is valid


hint4:
int lastSeenIndex=-1;
int minDist = Integer.MAX_VALUE;
if(arr[i]==x || arr[i]==y){
    if(lastSeenIndex!=-1 && arr[lastSeenIndex]!=arr[i]){
        minDist = Math.min(minDist, i - lastSeenIndex);
    }
    lastSeenIndex=i; // Do not forget to Update lastSeenIndex everytime you see x or y
}
```

# Leaders in an array
```
You are given an array arr of positive integers. Your task is to find all the leaders in the array. An element is considered a leader if it is greater than or equal to all elements to its right. The rightmost element is always a leader.

Input: arr = [16, 17, 4, 3, 5, 2]
Output: [17, 5, 2]
```
```
Hint1: Traverse from right to left keeping track of max so far. By default, last element is always a leader since there is no one to the right!

Hint2: whenever max gets updated from right to left, you found a leader!

Code skipped as its simple.
```
# Alternative Positive Negative
```
Given an unsorted array arr containing both positive and negative numbers. Your task is to rearrange the array and convert it into an array of alternate positive and negative numbers without changing the relative order.

- NOTE: 0 is to be treated as positive

Input: arr[] = [9, 4, -2, -1, 5, 0, -5, -3, 2]
Output: [9, -2, 4, -1, 5, -5, 0, -3, 2]
Time Complexity: O(n)
Recommended Auxiliary Space: O(1)
```
```
Simple solution Using O(n) space
Hint1:
WE could simply add positive and negative numbers to separate lists
Then if its even index, fetch from positive list
If its odd index, fetch from negative list

```
### How to right rotate an array by 1?
```
[9,4,6,-2] -> [-2,9,4,6]
```
```
temp = arr[N-1]
arr[i]=arr[i-1], for i=N-1 till 1
arr[0]=temp
```
