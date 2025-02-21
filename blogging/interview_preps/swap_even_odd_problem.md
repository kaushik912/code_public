
### Problem 

Rearrange array in such a way that all even numbers are to the left and odd numbers are to the right.

The problem requires rearranging an array such that **all even numbers appear before odd numbers** while maintaining efficiency. Here are some useful hints to guide your approach:

### **Hints:**
1. **Understand Even and Odd:**  
   - Even numbers are those divisible by 2 (`num % 2 == 0`).  
   - Odd numbers are those not divisible by 2 (`num % 2 != 0`).  

2. **Brute Force Approach (O(n) extra space, O(n) time):**  
   - Use two separate lists: one for evens and one for odds.  
   - Concatenate the two lists at the end.  
   - This is **not in-place**, so it requires extra space.

3. **Two-Pointer Approach (O(1) space, O(n) time, in-place):**  
   - Use **two pointers**:  
     - `left` starts at the beginning and moves forward when it sees an even number.  
     - `right` starts at the end and moves backward when it sees an odd number.  
   - Swap elements when `left` is at an odd number and `right` is at an even number.  
   - Stop when `left >= right`.

4. **Partitioning Approach (Like QuickSort's Partition, O(n) time, in-place):**  
   - Use a single pointer to **partition** the array in one pass.  
   - Iterate and place even numbers in the correct section while shifting odd numbers.

5. **Edge Cases to Consider:**  
   - An array where all elements are already even (`[2, 4, 6, 8]`) → No changes needed.  
   - An array where all elements are already odd (`[1, 3, 5, 7]`) → No changes needed.  
   - An array with a mix but already partitioned (`[2, 4, 6, 1, 3, 5]`) → No swaps needed.  
   - An empty array (`[]`) or single-element array (`[1]` or `[2]`).  



