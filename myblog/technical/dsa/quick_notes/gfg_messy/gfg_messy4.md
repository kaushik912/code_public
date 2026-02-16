### Move All Zeroes to End

You are given an array arr[] of non-negative integers. You have to move all the zeros in the array to the right end while maintaining the relative order of the non-zero elements. The operation must be performed in place, meaning you should not use extra space for another array.

// Hint1: Use a two-pointer approach, both from left.
// One traverses the array and other only overwrites and moves when the traversal sees an non-zero

// Hint2:
// Think of a pointer where the next non-zero will go. 
// Every time you see a non-zero number,
// you place that number in that pointer and move that pointer forward.
    
// if arr[i]!=0 ,  arr[nonZeroIndex++] = arr[i]
    
// Working Example    
//  [1, 2, 0, 4, 3, 0, 5, 0]
// [1,2,4,4,3,0,5,0], i=3, nonZeroIndex=2, copy the value and move nonZeroIndex pointer
// [1,2,4,3,3,0,5,0], i=5, nonZeroIndex=3, same as above
// [1,2,4,3,5,0,5,0], i=6, nonZeroIndex=4, same as above
// at this point,i=7 has reached the end of array
// copy from nonZeroIndex till end, zeroes

### Indexes of Subarray Sum
// sliding window concept
// left = 0
// right = 0
// expand right to include new elements
// window= right-left+1
// if runningSum > target, shrink window from left until runningSum<target (loop)
// if runningSum==target, we reached the solution

### Rearrange Array Alternately
Given an array of positive integers. Your task is to rearrange the array elements alternatively i.e. first element should be the max value, the second should be the min value, the third should be the second max, the fourth should be the second min, and so on.

Input: arr[] = [1, 2, 3, 4, 5, 6]
Output: [6, 1, 5, 2, 4, 3]

// first sort the input array
// maxIdx = arr.length-1
// minIdx = 0
// maxElem = arr[arr.length-1]+1, this is required for mod calculations

// Formula part:
// arr[i] = arr[i] + (new_value % maxElem) * maxElem;
// new_value is  
    // arr[maxIdx--] if i is even, 
    // arr[minIdx++] if i is odd

// decode:  
// arr[i] / maxElem gives the new value

### Find First and Last Position of Element in Sorted Array

//[5,7,7,8,8,10]
// mid = 5/2 = 2, target = 8
// arr[mid]=7,
// target > arr[mid], we need to look in right part
// low = mid+1
// low = 3, high = 5, mid = 4
// arr[4]=8 == target

// So initially binary search to match the target
// there are two possibilities
    // if there is a value to left, we could continue the search by setting high=mid-1
    // if there is a value to right, we could continue the search by setting low = mid+1
    // update the result if there is a match found in both cases
    // So pass a boolean isFirst that if true, looks to left otherwise it looks to right
    //basically continue binary search by adjusting the low and high and update result.

