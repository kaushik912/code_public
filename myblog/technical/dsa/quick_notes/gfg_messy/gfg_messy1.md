## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

-  This one is for `GFG` questions in no particular order

# Problem: Replace all 0's with 5
You are given an integer n. You need to convert all zeroes of n to 5.
Input: n = 1004
Output: 1554

### Quick exercise( observe pattern):

- num=1004

- 1004%10, rem=4, num=1004/10 = 100, if rem!=0, 10^0*4
- 100%10, rem=0, num=100/10=10, if rem=0, 10^1*5 
- 10%10, rem=0, num=10/10=1, if rem=0, 10^2*5
- 1%10, rem=1, num=1/10=0, if rem!=0, 10^3*1
- stop when num=0

- Use this approach to calculate newSum by adding each digit with power logic.
- initialize some k=0,
- Assume newSum=0
    - if rem is 0, newSum+= (10^k++)*5 
    - else,  newSum+=(10^k++)*rem

- Central idea is to use mod and div operations on a number to traverse from right to left.
- If we see a rem=0, then replace that with 5 but adjust the position using power logic.
- For rem!=0, replace the same rem value with position using power logic.

- One special case
    - when n=0, simply return `5`
    - This isn't handled by the modulo logic!

# find equilibrium point in an array
Given an array of integers arr[], the task is to find the first equilibrium point in the array.

The equilibrium point in an array is an index (0-based indexing) such that the sum of all elements before that index is the same as the sum of elements after it. Return -1 if no such point exists. 

Input: arr[] = [1, 2, 0, 3]
```
calculate sum = 6
lets iterate over i from 0 to end.
i=0, leftSum=0, rightSum = sum - leftSum-arr[i] = 6 - 0 - 1 = 5
i=1, leftSum+=(arr[i-1] provided i-1>=0),
    leftSum= 1, rightSum = 6 - 1 - 2 = 3
i=2, leftSum+=(arr[i-1] provided i-1>=0),
    leftSum=3, rightSum = 6 - 3 - 0 = 3
    if leftSum==rightSum
        we have reached equilibrium point.

Lets try one more
Input: arr[] = [-7, 1, 5, 2, -4, 3, 0]
sum=0

i=0, leftSum=0, rightSum = 0 - 0 -(-7) = 7
i=1, leftSum = -7, rightSum = 0 -(-7)-1 = 6
i=2, leftSum= -6, rightSum = 0 -(-6)-5 = 1
i=3, leftSum=-1, rightSum = 0 -(-1)-2 = -1

So, idea is to calculate leftSum correctly.
I have used leftSum+=(arr[i-1] provided i-1>=0)
this skips the first one and calculates from 2nd index onward.

```

# Find third largest element 
Given an array, arr of positive integers. 
Find the third largest element in it. Return -1 if the third largest element is not found.
Expected Time Complexity: O(n)
Expected Space Complexity: O(1)

Input: arr[] = [2, 4, 1, 3, 5]
Output: 3

```
- maintain 3 values, say i1,i2,i3
- i1 is largest, i2 is 2nd largest, i3 is 3rd largest
- we use logic to "trickle down"
- if we see a new max (>=i1), we make 
    - i3=i2
    - i2=i1
    - i1=max
    - This is the central idea 
```

### Working example
- initially, 
    i1=-1
    i2=-1
    i3=-1

- 2 comes,
    so, i3=-1, i2=-1, i1=2
- comes 4 (greater than i1),
    so i3=-1, i2=2, i1=4
- comes 1
    its not greater than i1 
    its not greater than i2
    i3 is still -1, we i3 takes that value, i3=1
    so, now i3=1, i2=2, i1=4
- comes 3
    - its not greater than i1
    - but its greater than i2=2
    - so 
        i3=2, 
        i2=3,
        i1=4 (unaffected)
- comes 5
    - its greater than i1!
    - i3=i2 = 3
    - i2 = i1= 4
    - i1= 5 
    so finally, i1=5, i2=4, i3=3

So third-largest element is 3

- So intuitively, if a new max arrives
    - third becomes second
    - second becomes first
    - first takes new max value
Similarly for secondMax and thirdMax.

# Max and SecondMax
Given an array arr[] of positive integers which may have duplicates. The task is to find the maximum and second maximum from the array, and both of them should be different from each other, and If no second maximum exists, then the second maximum will be -1.

Input: arr[] = [2, 1, 2]
Output: [2, 1]

Input: arr[] = [3, 3, 3]
Output: [3, -1]

- We could extend the same example as before
- instead of 3 values, we could use two values, i1 and i2 
- use the same `trickle down` approach
- Since we only want "distinct" values, we need to use strictly ">" comparison.

## Working Example for distinct
-  comes 2,
    i2=-1, i1=2
 - Comes 1
    i1=2, i2=1
- Comes 2
    i1=2, 
    i2=?,
    - essentially, only if i2 < arr[i] < i1
    - update i2 = arr[i],
    - Since arr[i]=2, and i1 =2, we don't update i2
    - i2=1

- i1,i2=-1
- if (arr[i] > i1){
    i2=i1;
    i1=arr[i]
}else if (arr[i]< i1 && arr[i] > i2){
    i2=arr[i];
}

# Min distance in array
You are given an array, arr[]. Find the minimum index based distance between two distinct elements of the array, x and y. Return -1, if either x or y does not exist in the array.

Input: arr[] = [1, 2, 3, 2, 1 ], x = 1, y = 2
Output: 1

Explanation: x = 1 and y = 2. 
There are two distances between x and y, which are 1 and 3 out of which the least is 1.

### Approach
- last=-1, min=INT.MAX_VALUE;

- last is the recent index of x or y

- if arr[i]!='x' or arr[i]!='y'
    - skip

- if last=-1 and (arr[i]=='x' or arr[i]=='y') (first time)
    - then last = i

- else if we see an arr[i] which is different from arr[last],
    - say, we set last for 'x'
    - now we see i for 'y'
    - then we got a pair, we can calculate the difference as (i-last)
    - if this difference < min, update min
    - reset 'last' to this i ( so it becomes 'y')
    - next time, we'll look for 'x' and calculate the diff and see if the minimum is lower
- else if we see an arr[i] same as arr[last]
    - simply update last to i
    - we would be going "nearer" to the next possible pair.


### Working Example
- Input: arr[] = [1, 2, 3, 2, 1 ], x = 1, y = 2
- last=-1, min=INT.MAX_VALUE;
- i=0, arr[0]=1=x, last=0,
    - we have set last to point to x
- Now, arr[i]=2='y' and arr[i]!=arr[last], 
    - we got a pair
    - calculate diff = (i-last) = 1-0 = 1
    - update min
        - min = Math.min(min, diff) = 1
    - last = i = 1
    - Now we have set last to point to 'y'
- comes 3,
    - no effect, simply skip
- Comes 2,
    - no effect, because arr[3]=2 is same as arr[last], so no new pair!
    - but we update last to 3 so that we get "nearer" to next pair.
    - last = 3
- Comes 1,
    - arr[4]=1,
    - diff = 4- 3 = 1
    - min is again at 1
- So min is 1

### Key Idea
- Use a index 'last' to track either 'x' or 'y'
- initially last=-1

- If arr[i] is not 'x' or 'y',simply skip the iteration

- lets say we first encounter 'x' ( last==-1)
    - last = xIndex, 
    - we can't compute any diff 
- For any subsequent match of either 'x' or 'y' at index i
    - if its completes a "pair" ( arr[i]!=arr[last] , so it's other value in pair!)
        - diff =  i - last
        - min = Math.min(min, diff)
        - last =i
    - if not completing a pair
        - still, last=i
        - it may help us get "nearer" to next pair
- I explicitly add last=i twice for ease of understanding. It could be merged into single statement later.

# Leaders in an array

You are given an array arr of positive integers. Your task is to find all the leaders in the array. An element is considered a leader if it is greater than or equal to all elements to its right. The rightmost element is always a leader.

Input: arr = [16, 17, 4, 3, 5, 2]
Output: [17, 5, 2]

## Approach
- Start from right to left
- always last element is a leader as there is no one to its right!
- 2 is a leader, 
- lets store leader=2 as the most recently seen leader 
- now comes 5
    - 5 is greater than 2
    - so 5 is also a leader.
    - now add 5 to our result list  ( {2,5,})
    - now, leader = 5 (recently seen leader)
- now comes 3
    - Its lower than leader, so it can't be a leader
- now comes 4
    - Same as before
- now comes 17
    - 17 > 5, so 
    - 17 is also a leader
    - add 17 to our list. ({2,5,17})
    - now leader=17
- now comes 16
    - 16 < leader, so cannot be a new leader

Now , to match output, we can reverse our list: {17,5,2}
