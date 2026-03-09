## Swap Even Odd Problem
```
Rearrange array in such a way that all even numbers are to the left and odd numbers are to the right.
eg: [13, 10, 20, 21]
Expected: [20, 10, 13, 21]
BONUS: Try to do it in-place without using extra space
```
```
Hint1:
A naive approach would be to maintain two lists , one for even and other for odd.

so,
evens: {10,20}
odds: {13,21}

simply append evens first followed by odds. 
[10,20,13,21]

This takes O(n) extra space.
But time complexity is O(n).
```
```
Hint2: How about using a 2-pointer approach? 
That way we won't need extra space.

eg: [13, 10, 20, 21]
left=0, right=N-1

So, left side we expect number to be even. 
Right side we expect number to be odd.
if there is a mismatch, we simply swap.

initially, we see left is pointing to 13 (odd but it should be even)
right points to 21 (odd, its good, so right--)
right points to 20 (even!, thats not good)

Its time to swap, so it becomes:
[20,10,13,21]

post swap, we move left++, right--
at this point, left ==right

Hint3: When will be stop using the 2-pointer?
while(left<right){
    //do the swaps 
}
left==right, the swap will have no effect. So we can ignore this.

Hint4: Implement the solution

int left=0;
int right=N-1;
while(left<right){
    if(arr[left]%2==0){
        //left is already even
        left++;
    }
    else if(arr[right]%2!=0){
        //right is already odd
        right--;
    }
    else if(arr[left]%2!=0 && arr[right]%2==0){
        //swap left and right
        swap(arr,left,right);
        left++;
        right--;
    }
}

Hint5: Tiny Optimization, use else for last part.

int left=0;
int right=N-1;
while(left<right){
    if(arr[left]%2==0){
        //left is already even
        left++;
    }
    else if(arr[right]%2!=0){
        //right is already odd
        right--;
    }
    else {
        // This is the case when they are in wrong places.
        //swap left and right
        swap(arr,left,right);
        left++;
        right--;
    }
}

```