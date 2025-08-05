## Equilibrium Point
Given an array of integers arr[], the task is to find the first equilibrium point in the array.

The equilibrium point in an array is an index (0-based indexing) such that the sum of all elements before that index is the same as the sum of elements after it. Return -1 if no such point exists. 

---

### 🧠 **Equilibrium Point – Quick Hint (Flash Card)**

* Compute total sum of array.
* For each index `i`, check:
  - `rightSum = totalSum - leftSum - arr[i]`
  - If **`leftSum == rightSum`**, then index `i` is the equilibrium point.
* Update: **`leftSum += arr[i]`** as you move forward.

---
