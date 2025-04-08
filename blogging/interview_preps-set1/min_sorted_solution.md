```java
class FindMinimumInRotatedSortedArray {
    public static int findMin(int[] nums) {
        int left = 0, right = nums.length - 1;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            // If mid element is greater than the rightmost element, minimum is on the right half
            if (nums[mid] > nums[right]) {
                left = mid + 1;
            } else {
                // Otherwise, minimum is on the left half (including mid)
                right = mid;
            }
        }
        
        return nums[left]; // left will point to the minimum element
    }

    public static void main(String[] args) {
        // Test cases
        int[] arr1 = {3, 4, 5, 1, 2}; // Rotated case
        int[] arr2 = {4, 5, 6, 7, 0, 1, 2}; // Another rotated case
        int[] arr3 = {11, 13, 15, 17}; // Already sorted case (no rotation)
        int[] arr4 = {2, 1}; // Smallest case with rotation
        int[] arr5 = {1}; // Single element case

        // Printing results
        System.out.println("Minimum in arr1: " + findMin(arr1)); // Expected: 1
        System.out.println("Minimum in arr2: " + findMin(arr2)); // Expected: 0
        System.out.println("Minimum in arr3: " + findMin(arr3)); // Expected: 11
        System.out.println("Minimum in arr4: " + findMin(arr4)); // Expected: 1
        System.out.println("Minimum in arr5: " + findMin(arr5)); // Expected: 1
    }
}
```
