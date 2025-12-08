# DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

## Write program to add two linked lists
- The digits are stored in reverse order, and each of their nodes contains a single digit.
- Add the two numbers and return the sum as a linked list.
example: 
- L1 = 2 -> 4 -> 3
- L2 = 5 -> 6 -> 4
- Output: 7 -> 0 -> 8

```
lets say ,l1 for list1, l2 for list2
start from left,  
initially carry=0
Keep going until both lists are consumed
    // while (l1!null || l2!=null)
 if both lists are non-empty
     calculate sum by adding each node's value + carry(0 or 1).
     move both pointers
 else if l1 is not empty,
   calculate sum by adding l1's value + carry(0 or 1).
   move only l1
 else 
  //l2 is only not empty
   calculate sum by adding l2s value + carry(0 or 1).
   move only l2
  
  newVal = sum%10
  add newVal to a new list's result
if sum > 9 (there's a overfleft)
   carry=1
else
   carry=0

//after loop,
if carry is still present, 
 add a new node with value 1 to new list.
```


## find min value in a sorted array

#### Intuition
- The min value is where the sort "breaks". Min value is also the "rotation point".
- Using binary search, we keep discarding the half that is fully sorted and focus on the "unsorted" half because that is where sort breaks and contains the minimum.
- Always compare mid with either "left" or "right" but not both. Any one end comparison is enough.

Working Examples
```
case: [4,5,1,2,3]

left=0
right=4
Now mid=2
arr[mid] < arr[right]
So mid..right is already sorted
So rotation must have happened in [left..mid]

We include mid also in the range. 
Why? because mid could also be the min element. 

Now, we have 4,5,1
Now left=0 right=2 so mid=1
arr[mid] > arr[right]

We see, left…mid is sorted
So we need to look in [mid+1..right]
Why (mid+1) ? 
because arr[mid] as its already greater than arr[right], so mid won't ever be minimum element.

So now, left=2, right=2 
Now solution is reached
1 is the min element
```

Example2: 
```
case2 : [6,1,2,3,4,5]
left=0, right=5
mid = 5/2=2
arr[mid]=2
arr[mid] < arr[right]
So, mid..right is sorted 
We need to look left for the "breaking" point where sort breaks.
so, we look in arr[left..mid],
left=0, right=2
[6,1,2]
Now, mid=1
arr[mid] < arr[right]
so, mid..right is sorted
so we again need to left in left.
So we look in [left..mid]
left=0, right=1
[6,1]
mid=0
Now, arr[mid] > arr[right]
so we need to look in the right
arr[mid+1..right]
left=1, right=1
mid=1
Now left is no longer less than right
So we have reached the minimum!
```

#### Summary

Intuitively, 
```
while left < right
    If arr[mid]< arr[right]
    // means mid..right is sorted
    // left..mid would contain min element
    // `mid` could itself be the min element
    else
    // arr[mid] > arr[right]
    // sort is broken and min would be in the right half
    // so, mid+1..right will contain min element
    // we choose `mid+1`  because arr[mid] itself is greater than arr[right] and so can't be a min element
```
