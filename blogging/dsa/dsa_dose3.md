## Reverse Array in place
When reversing a subarray **in-place**, you're always using the **two-pointer technique**:

* One pointer starts at the **beginning** (`start`).
* One pointer starts at the **end** (`end`).
* You **swap** elements at `start` and `end`.
* Then move:

  * `start++`
  * `end--`

This continues **until `start >= end`**, which means you've reached (or passed) the **middle** of the subarray.

## Rotate Array
Given an array arr[]. Rotate the array to the left (counter-clockwise direction) by d steps, where d is a positive integer. 
Do the mentioned change in the array in place.

Note: Consider the array as circular.

🧠 **Flash Card: Left Rotate Array by `d` (In-Place, Circular)**

**Left Rotate Array by `d` (in-place)**

1. Compute `d = d % n`
2. Reverse first `d` elements
3. Reverse remaining `n - d` elements
4. Reverse the entire array

➡️ **Effectively rotates array left by `d` positions**

### 💡 Example:

Array: `[1, 2, 3, 4, 5]`, `d = 7`

Length `n = 5`, so `d = 7 % 5 = 2`

\=> Rotate left by 2 steps → `[3, 4, 5, 1, 2]`




