# DSA quick messy notes
- Writing your own understanding is important.
- Each person has his own perspective on the algorithm logic. So even if messy notes, its still a good idea.
- For quick testing or validation, use online IDE like: https://www.onlinegdb.com/online_java_compiler

## Write program to add two linked lists

```
- The digits are stored in reverse order, and each of their nodes contains a single digit.
- Add the two numbers and return the sum as a linked list.
example: 
- L1 = 2 -> 4 -> 3
- L2 = 5 -> 6 -> 4
- Output: 7 -> 0 -> 8
```

```
Hint1:
this is simple left to right addition with carry

Hint2:
What happens when we add 6+4?
that particular place would have : (6+4)%10=0
carry= (6+4)/10 = 1

Hint3: what about the below case?
- L1 = 2 -> 4 
- L2 = 5 -> 6 -> 9
Always think of multiple examples
when 9 + 1 happens, both lists are finished yet carry remains.

Hint4: Use some neat tricks like dummy pointer
Start with a dummy node. 
populate values for the list additions as next pointers to this dummy.
And return dummy.next() as head 

Hint5: What kind of loop is good?
while (l1!=null || l2!=null || carry){
    //calculating digSum based on whichever values are available
}

Hint6: Put these ideas into action!

Node dummy = new Node(0);
Node curr = dummy;
int carry=0;
while(l1!=null || l2!=null || carry!=0){
    int digiSum=0;
    if(carry!=0){
        digiSum+=carry;
    }
    if(l1!=null){
        digiSum+=l1.val;
        l1=l1.next;
    }
    if(l2!=null){
        digiSum+=l2.val;
        l2=l2.next;
    }
    carry = digiSum/10;
    digiSum%=10;
    Node newNode = new Node(digiSum);
    curr.next = newNode;
    curr = curr.next;
}
return dummyNode.next;

```


## find min value in a sorted array
```
Given the sorted rotated array nums of unique elements, return the minimum element of this array.
Input: nums = [3,4,5,1,2]
Output: 1
```
```
Hint1: 
Since the array is sorted but rotated, we could employ binary search!

Hint2: 
Think where it will break the sort order. That's the min value!

Hint3: 
eg: [3,4,5,1,2], arr[mid] > arr[high], which is unusual for sorted array.
So, the min is located to the right. 
Also, arr[mid] can never be min since its already greater than arr[high].
we update search in (low = mid+1, high)

Hint4:
eg: [4,5,1,2,3], here arr[mid] < arr[high]
so that is not unusual, its sorted. WE need to look to left of mid (including mid!)
So we search in (low, high=mid)

Hint5:
Once low and high converge we have the minimum

Hint6: Put these ideas into action!
low = 0
high = N-1;
while(low<=high){
    if(low==high){
        //low and high have converged!
        return low;
    }
    int mid = (low+high)/2;
    if(arr[mid] > arr[high]){
        //this is unusual, so look to the right
        low = mid+1;
    }else if(arr[mid] < arr[high]){
        // this is normal sorted part, look to the left
        high = mid;
    }
}
```
## Trapping Rain water
```
You’re given an array height[] where each element represents the height of a bar in a histogram.
After raining, how much water is trapped between the bars?
Input: arr[] = [3, 0, 1, 0, 4, 0, 2]
Output: 10
Explanation: The expected rainwater to be trapped is shown in the above image.
```
Hint1: 
Visualize
[trapping.png](trapping.png)

```
Hint2: 
For each index, the water trapped depends on the tallest bar to the left and tallest bar to the right.

Hint3: 
Think brute force 
For a given index i, i could identify leftMost max and rightMost max

lets say , its leftMax and rightMax respectively.
Water trapped at i= Math.min(leftMax,rightMax) - arr[i]; //subtract from the height of that bar itself

for index i,
    for j =0 ;j < i; findLeftMax
    for j=i+1, j<N; findRightMax

So it takes O(N^2) time

Also, overall water calculation is from i=1 to N-2

Hint4: 
Pre-calculate leftMax and rightMax at each index
Then the formula becomes:
water_trapped[i]+= Math.min(leftMax[i],rightMax[i])-arr[i];

Hint5: 
How do we pre-calculate leftMax and rightMax?
[3,0,1,0,4,0,2]

leftMaxVal=arr[0]//initially
i=1 till N-1
    leftMaxVal = Math.max(leftMaxVal,arr[i]);
    leftMax[i] =leftMaxVal;

rightMaxVal = arr[N-1]; //initially
i=N-2 till 0
    rightMaxVal = Math.max(rightMaxVal, arr[i]);
    rightMax[i] = rightMaxVal;

For our example,
[3,0,1,0,4,0,2]
leftMax = [3,3,3,3,4,4,4]
rightMax = [4,4,4,4,4,2,2]

Hint6: Calculate water trapped between leftmost and rightmost bars.
We don't worry about 0 and N-1 as there is no water ever trapped in these two columns.
so, i = 1 to N-2 
    calculate_water_trapped

Hint7: Put these ideas into action

int[] leftMax = new int[height.length];
int[] rightMax = new int[height.length];

int leftMaxVal=height[0];
for(int i=1;i<height.length;i++){
    leftMaxVal = Math.max(leftMaxVal,height[i]);
    leftMax[i] = leftMaxVal;
}

int rightMaxVal=height[height.length-1];
for(int i=height.length-2;i>=0;i--){
    rightMaxVal = Math.max(rightMaxVal, height[i]);
    rightMax[i] = rightMaxVal;
}

for(int i=1;i<height.length-1;i++){
    water+=(Math.min(rightMax[i],leftMax[i])-height[i]);
}

Hint8: Can we do better?
We could use the fact that leftMax[i] already holds the max Height seen so far from left.
So we could use DP-kind of approach.

leftMax[0]=height[0]; //base case
for(int i=1;i<height.length;i++){
    leftMax[i] =  Math.max(leftMax[i-1],height[i]);
}

Similarly for rightMax,

rightMax[height.length-1]=height[height.length-1]; //base case
for(int i=height.length-2;i>=0;i--){
    rightMax[i] = Math.max(rightMax[i+1], height[i]);
}

Since we are iterating and updating backwards, rightMax[i+1] holds what max right we have seen so far until i.

Hint9:
Previous approach  of using rightMaxVal, leftMaxValue is also fine. It just uses one extra variable to keep track of max-so-far.

You can choose simplicity over brevity if its easier to understand code-wise.( you can always optimize later!)

```