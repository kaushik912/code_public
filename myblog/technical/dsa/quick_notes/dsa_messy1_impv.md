## DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

### write program to print all permutations of {1,2,3}

```
Hint1: Think about how will you permute two numbers    
[1,2]
swap 0 with 0
swap 0 with 1
[1,2]
[2,1]

Hint2: Extend to 3 numbers

[1,2,3]
 swap 0 with 0, permute on remaining
 [1],permute(2,3)
 we already solved this before for two numbers,
    [1], [2,3]
    [1], [3,2]
    Now, we need to revert this back to original
    [1][2,3] , achieved by a re-swap
 //technically there is also a re-swap at outer layer but since its 0,0 , it has no effect

 swap 0 with 1, permute on remaining
 [2], permute(1,3)
 We again already solved this before for 2 numbers
    [2], [1,3]
    [2], [3,1]
    again, we re-swap to get back to original order 
    [2][1,3] -> inner re-swap
 [1][2,3] -> outer re-swap

Hint3: We see a pattern above, now generalize it

initially l=0, r=Len-1

permute(str,l,r)
 if(l==r)
    print str
    return ;
 
 for i in l to r
    swap(str,l,i);//swap i with l
    permute(str,l+1,r); permute on remaining
    swap(str,l,i); //restore back

- I admit this is a bit of abstract thinking as it involves recursion + backtracking!
```

# find median in a stream of numbers

```
Input:  arr[] = [5, 15, 1, 3, 2, 8]
Output: [5.00, 10.00, 5.00, 4.00, 3.00, 4.00] 
```
```
Hint1: Suppose we maintain two heaps. min-heap and max-heap.

Lets say we have N elements now.

min-heap stores the highest N/2 elements (using the "survival of fittest", all weak keys are eliminated while adding, so it retains the highest keys)

max-heap stores the lowest N/2 elements.

Hint2: imagine the array as [max-heap(lower) , min-heap(upper)],
Assume that median lies in lower half , ie. part of max-heap.
if length is even, these two heaps will be of equal size.
if length is odd, since median lies in lower half , max-heap.size - min-heap.size = 1
So these two heaps are either equal or atmost differ by 1.
so,0 <= (max-heap.size - min-heap.size) <=1
So, max-heap.size > min-heap.size 

Hint3: max-heap.peek() <= min-heap.peek()
max-heap's highest element should be less than min-heap's lowest element

Hint4: Do a dry-run on [5,15,1,3]

While adding a number, check if its greater than min-heap's peek, if yes, then it should go to min-heap.
otherwise it should go to max-heap.

add 5 to max-heap
max-heap.size - min-heap.size = 1, so its balanced.
Median is max-heap.root element = 5

Add 15 to max-heap
max-heap: [15,5]
max-heap.size - min-heap.size = 2, so not balanced!

Extract from max-heap and insert into min-heap
max-heap:[5], min-heap:[15]
now, max-heap.size - min-heap.size =0, so we need to take average
median = 20/2 = 10

Add 1 to max-heap again
max-heap:[5,1], min-heap:[15]
so heap.size.difference = 1, 
median = 5 (max-heap root element)

Add 3 to max-heap 
max-heap:[5,3,1], min-heap:[15]
unbalanced again, so we need to balance.
max-heap:[3,1], min-heap:[5,15]
So, heap.size.diff=0, we need to take average
median = (3+5)/2= 4

Hint5: Generalize the above idea

Maintain two heaps, min-heap and max-heap

if the number > min-heap.peek(), it should go to min-heap
otherwise it should go to max-heap.

This will ensure that min-heap.peek() > max-heap.peek() --> RULE1

we know that max-heap.size >= min-heap.size

// CHECK BOTH WAYS AND BALANCE
if (max-heap.size < min-heap.size)  --> RULE2
    // min-heap contains more elements than max-heap
    extract root element from min-heap
    insert that into max-heap
if ( max-heap.size - min-heap.size > 1) --> RULE3
    // max-heap contains more elements
    extract root element from max-heap
    insert into min-heap

//calculate median
check if max-heap.size - min-heap.size==0, 
    median is average of both roots
else if max-heap.size - min-heap.size==1
    median is max-heap.root

Hint6: Java-specific

PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a,b)->b.compareTo(a));

```


# find k-largest numbers
```
Given an integer array nums and an integer k, return the kth largest element in the array.
Input: nums = [3,2,1,5,6,4], k = 2
Output: 5
```
```
Hint1: 
- We use a min-heap (survival of fittest where the weaker keys are removed)

Hint2:
eg: k=2, [3,2,1,5,6,4]
- initially it will be [2,3]
- Then when we try to add 1, its lower than peek, so will be skipped
- Then we try to add 5, since k=2(max-capacity), it will remove 2 and insert 5
- heap becomes [3,5]
- So weaker keys get removed with stronger ones.
- Now comes 6, it will remove 3 and insert 6 into the heap.
- heap becomes [5,6]
- 4 is ignored as its lesser than peek

- Kth element is simply the peek element

Hint3: Extending the above idea into code

PriorityQueue<Integer> p  = new PriorityQueue<>();
for(int i=0;i<nums.length;i++){
    if(p.size()==k){
        if(nums[i]<p.peek()){
            continue;
        }else{
            //survival of fittest, remove weaker keys and replace with stronger ones
            p.poll();
            p.offer(nums[i]);
        }
    }else{
        p.offer(nums[i]);
    }
}

return p.peek();

```


### Longest string without repeating characters
```
Given a string s, find the length of the longest substring without duplicate characters.
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc"

Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke"
```
```
Hint1: analyze "abacd"
moment we see another 'a', we adjust the window to exclude the previous 'a'
Think "indexes".

Hint2: use two pointers, left=0 , right=0 and map to store {char,index}
For "abacd", consider a point when map: {a:0,b:1},left=0 , right=2
now,since 'a' is duplicate, we adjust left = map.get('a')+1
and also update the a's new in the map index
so, left=1, right=2, map: {a:2,b:1}

Hint3: analyze "abcbaz"
Here: consider a point where 'b' repeats:
left=0, right=3, {a:0,b:1,c:1}
we could move left now as :
left = map.get('b')+1 
so, left=2, right=3, map:{a:0,b:3,c:1}
now we see a 'a'
left = map.get('a)+1 = 1.
Now our left is already at 2 , new left is 1.
This is an important pattern.
So we should not update left since we are already ahead.
so, left = Math.max( map.get(ch)+1, left);

Hint4: Calculate length and update maxLen
length of non-repeating string is (right-left+1) at every iteration while we process characters.

Hint5: Put above ideas into practice
left=0
right=0
maxLen=0
Map <Character,Integer> map = new HashMap<>();
while(right < N){
    char ch = s.charAt(right);
    if(map.containsKey(ch)){
        left = Math.max(map.get(ch)+1,left);
        map.put(ch,right);
    }else{
        map.put(ch,right);
    }
    int len = right-left+1;
    maxLen = Math.max(maxLen,len);
    right++;
}

```