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