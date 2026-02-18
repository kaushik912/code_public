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

### Merge two sorted arrays

#### General approach ( with auxilliary array)
// assume we have nums1[] and nums2[] are two sorted arrays
// assume nums[] is aux array, k its index.
// i runs for nums1, j runs for nums2
// while(i<m && j<n )
    // whichever is lower, copy that value to nums[k++]
        //whichever is lower, increment that index (i or j)
    // if both values are equal
        // copy twice into the nums[k++]
        // increment both i and j
// copy the left-overs to nums[k++]
    // while(i<n) nums1[i++]=nums[k++]
    // while (j<n ) nums2[j++]=nums[k++]


#### Approach without auxiliary array
// if nums1 is having length of (m+n)
// and nums2 is having length n
    //assume after m, all are zeroes
    //eg: nums1= [1, 2, 3, 0, 0, 0], nums2= [2,5,6]
// we need to do it in-place
//KEY IDEA: approach is to go backwards instead of forward
    // i = m-1
    // j = n-1
    // k = m+n-1
    // while i>=0 && j>=0
        // compare which is greater ( since we are filling backwards)
            // greater one gets copied at k
            // nums1[k--]= either nums1[i--] or nums2[j--]
        // if both are equal
            // copy twice into nums1[k--], decrement both i and j
    // Copy left-over items in nums2 into nums1
        // while(j<n) nums1[k--]=nums2[j--]
    
    // Why copy only for nums2?
    eg2: nums1= [5,6,7,0,0,0], nums2=[1,3,5]
    After 3 iterations, the nums1 is [5,6,5,5,6,7]
    // at this point, i=-1, j=1

    // but nums2 still has some elements left [1,3]
    //we need to copy left-over items in nums2 if present into num1
    // Finally it becomes [1,3,5,5,6,7]

    // KEY INTUITON:
    // if you have reached end of nums1(i=-1), that means all elements in nums1 have been processed but still if j>=0, then those elements in nums2 still need to be processed. Hence the need to loop over nums2

    //What if flip the arrays?
    eg3: nums1= [1,3,5,0,0,0], nums2=[5,6,7]
    // after 3 iterations, nums1= [1,3,5,5,6,7]
    // again j=-1, i=1
    // no need to copy left over in nums1 as all elements are already in place