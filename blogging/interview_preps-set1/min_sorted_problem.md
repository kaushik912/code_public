### Problem 

Find Minimum in Rotated Sorted Array

### Hints
The problem **"Find Minimum in Rotated Sorted Array"** is a classic binary search problem. Here are some hints to help you solve it efficiently:

### **Hints:**
1. **Understand Rotation:**  
   - The given array is **sorted** but has been **rotated** at some pivot unknown to you.  
   - Example: `[4,5,6,7,0,1,2]` → This was `[0,1,2,4,5,6,7]` before rotation.

2. **Observe the Properties of the Array:**  
   - The array is **partially sorted**: One half is always sorted, while the other half contains the minimum element.
   - If the array is **not rotated** (e.g., `[1,2,3,4,5]`), then the first element is the minimum.

3. **Binary Search Approach (O(log n)):**  
   - **Find the middle element (`mid`).**  
   - **Check if `mid` is the minimum:** If `nums[mid]` is smaller than `nums[mid - 1]` (exists), then `nums[mid]` is the minimum.  
   - **Decide which half to search:**  
     - If `nums[mid] > nums[right]`, the minimum is in the **right half** (move left pointer to `mid + 1`).  
     - Otherwise, the minimum is in the **left half** (move right pointer to `mid`).  

4. **Edge Cases to Consider:**  
   - An already sorted array (`[1,2,3,4,5]`) → First element is the minimum.  
   - A single-element array (`[5]`) → That element is the minimum.  
   - An array with two elements (`[2,1]`) → The smaller one is the minimum.  

Would you like a step-by-step breakdown of the binary search approach? 🚀
