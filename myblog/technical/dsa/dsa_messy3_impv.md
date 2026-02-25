## Sort 0s, 1s and 2s
```
Given an array arr[] containing only 0s, 1s, and 2s. Sort the array in ascending order.
Note: You need to solve this problem without utilizing the built-in sort function
```
```
Hint1: Since there are only three values, we could think 3 "regions" (low, mid and high)
So we can have three pointers: low, mid and high
low=0, mid = 0 (yes!), high= N-1

Hint2: Think some rules

anything left of low is always 0s.
mid is the "explorer" or "scanner" part. It starts with 0 and moves through array to inspect every element.
anything right of high is always 2.

Hint3: Think some swapping rules

assume at some time, we are at mid, and arr[mid]=0, 
But 0 should be in the low region.
So, we swap arr[mid] with arr[low]
mid has been processed now, mid++
low++, since anything before low is always 0s.

assume, we are again at mid but arr[mid]=1
low remains same
mid++ ( mid has been processed)
  
assume, we are again at mid but arr[mid]=2
But it should be in right region
swap arr[mid] with arr[high]
high--( anything right of high should be 2s)
should we increment mid?
What if arr[mid]=0 after swapping? won't that fail the low rule if we incremented mid?
so, no mid++ required.

Hint4: Put these swapping rules into action!

if arr[mid]==0,
  swap(arr,mid,low)
  mid++
  low++
if arr[mid]==1
  mid++
if arr[mid]==2
  swap(arr,mid,high)
  high--

Hint5: Since mid is our scanner and is incremented, we need to stop at some point. When?
while( mid <= high)
 implement_swapping_rules


```
## Reverse Array in place
```
You are given an array of integers arr[]. You have to reverse the given array.
```
```
Hint:
left=0
right=arr.length-1
while(left<=right)
  swap(arr,left++,right--);
```

## Rotate Array
```
Given an array arr[]. Rotate the array to the left (counter-clockwise direction) by d steps, where d is a positive integer. 
Do the mentioned change in the array in place.
```
```
Hint1: Understand what is left rotation
[1,2,3,4], d=1
left element is knocked off, and placed at the right
Ans: [2,3,4,1]

Hint2: What if d > N, 
[1,2,3,4], d = 6
we need to bring it under N
d = d%N
d = 6%4 = 2
Ans: [3,4,1,2]

Hint3: How do you do the rotation?
[1,2,3,4], d = 2
expected ans: [3,4,1,2]
reverse d elements
[2,1,3,4]
reverse N-d elements
[2,1,4,3]
reverse the entire array
[3,4,1,2]

Hint4: Apply the idea into action
d = d%N;
reverse(arr,0,d-1); // reverse d elements
reverse(arr,d,N-1); // reverse N-d elements
reverse(arr,0,N-1);// reverse N

```

## Longest Consecutive Subsequence
```
Given an array arr[] of non-negative integers. Find the length of the longest sub-sequence such that elements in the subsequence are consecutive integers, the consecutive numbers can be in any order.

Input: nums = [100,4,200,1,3,2]
Output: 4
Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. Therefore its length is 4.
```

```
Hint1: 
Since they can be in any order, we could use a Set to track numbers.

Hint2:
Add all elements to a HashSet.

Hint3:
lets say we are having value arr[i] , 
  check if arr[i]-1 is present in set.
  if map.get(arr[i])==null
   map.put(arr[i]-1,arr[i]);
    //eg: {3:4}
  else
    // eg: arr[i]=3
    oldVal = map.get(arr[i]); //4
    map.removeKey(arr[i]); 
    map.put(arr[i]-1,oldVal);//{2:4}

 eventually, you'll have {1:4}
so max length can be calculated.
 
```


