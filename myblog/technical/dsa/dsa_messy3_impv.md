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
consider the sequence: [1,3,4,2]

we update a map for each element as follows:
look for left and right of each element in the map.
  if present, we get its value.

So initially, {1:1, 3:1}

When we see a 4, we see left=3 already exists in the map.
newLen = 1+left_len = 1+1 = 2
so we update, {1:1, 3:2,4:2}

Now we see a 2, left=1 and right=3
left_len =1
right_len =2

newLen = 1+2+1 = 4

We may be tempted to update {left:4, right:4}!

But we need to update the "boundaries", not just immediate left and right.
left_boundary = num-left_len = 2 - 1 = 1
right_boundary = num+right_len = 2+2 = 4

so instead we update: {1:4,4:4}

NOTE: if the key already exists in the map, we ignore.(to avoid double-updates)

Hint2:
We use the fact that for a "consecutive" subsequence for num, we look for left_subsequence length and right_subsequence length and we update that num's subsequence using:
num_len = left_len+right_len+1
Update the boundaries
map.put(num-left_len, num_len);
map.put(num+right_len,num_len);

Hint3:
We could track a maxLen to keep track of the max num_lens calculated so far and return the result.

Hint4: Implement these ideas in action!
Map<Integer,Integer> map = new HashMap<>();
int max = Integer.MIN_VALUE;
for(int num : nums){
  if(map.containsKey(num)){
    //skip to avoid any duplicate calculations
    continue;
  }
  int left_len = map.getOrDefault(num-1,0);
  int right_len = map.getOrDefault(num+1,0);
  int new_len = left_len + right_len + 1;
  max= Math.max(new_len,max);
  map.put(num,new_len);
  map.put(num-left_len,new_len);
  map.put(num+right_len,new_len);
}


```


