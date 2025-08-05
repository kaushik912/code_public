## Equilibrium Point
Given an array of integers arr[], the task is to find the first equilibrium point in the array.

The equilibrium point in an array is an index (0-based indexing) such that the sum of all elements before that index is the same as the sum of elements after it. Return -1 if no such point exists. 

### 🧠 **Equilibrium Point – Quick Hint (Flash Card)**

* Compute total sum of array.
* For each index `i`, check:
  - `rightSum = totalSum - leftSum - arr[i]`
  - If **`leftSum == rightSum`**, then index `i` is the equilibrium point.
* Update: **`leftSum += arr[i]`** as you move forward.

---
## Array Leaders
You are given an array arr of positive integers. 
Your task is to find all the leaders in the array. 
An element is considered a leader if it is greater than or equal to all elements to its right. 
The rightmost element is always a leader.

### 🧠 **Leaders in an Array – Quick Hint (Flash Card)**

* Traverse the array **from right to left**.
* Keep track of **`maxFromRight`**, initialized with the last element.
* If **`arr[i] >= maxFromRight`**, then `arr[i]` is a leader → update `maxFromRight = arr[i]`.

---
## Subarray with Given Sum
Given an array arr[] containing only non-negative integers, your task is to find a continuous subarray (a contiguous sequence of elements) whose sum equals a specified value target. 
You need to return the 1-based indices of the leftmost and rightmost elements of this subarray. 
You need to find the first subarray whose sum is equal to the target.

Note: If no such array is possible then, return [-1].

### 🧠 **Subarray with Given Sum (Non-negative Integers) – Quick Hint (Flash Card)**

* Use **sliding window**: maintain a `start` pointer and a running `currentSum`.
* Expand `end` and **add** `arr[end]` to `currentSum`.
* If `currentSum > target`, **shrink** the window from the left (`start++`) until `currentSum <= target`.
* If `currentSum == target`, record `start+1` and `end+1` as the answer (1-based index).
* Works efficiently in **O(n)** time when all numbers are **non-negative**.

---
## Sort 0s, 1s and 2s
Given an array arr[] containing only 0s, 1s, and 2s. Sort the array in ascending order.
Note: You need to solve this problem without utilizing the built-in sort function

### 🧠 **Sort 0s, 1s, and 2s – Quick Hint (Flash Card)**

* Use **Dutch National Flag Algorithm** with three pointers:
  **`low`, `mid`, and `high`**
* Loop while `mid <= high`:

  * If `arr[mid] == 0` → swap with `arr[low]`, increment both
  * If `arr[mid] == 1` → just move `mid`
  * If `arr[mid] == 2` → swap with `arr[high]`, decrement `high`

* This gives an in-place, **O(n)** solution with **no extra space**.

### 🔁 **Logic**

1. **If `arr[mid] == 0`**:

   * It's in the wrong region (should be left)
   * So we **swap with `arr[low]`**
   * Then, **increment both** `low` and `mid`

2. **If `arr[mid] == 1`**:

   * It's already in the correct middle region
   * Just **move `mid` forward**

3. **If `arr[mid] == 2`**:

   * It's in the wrong region (should be right)
   * So we **swap with `arr[high]`**
   * Then, **decrement `high`**
   * ⚠️ **Do not increment `mid`**, because the swapped value from `high` hasn’t been checked yet

### 📊 **Why This Works**

* We're always pushing 0s left and 2s right.
* 1s naturally settle in the middle.
* Once `mid > high`, the unknown region is fully processed, and the array is sorted.


