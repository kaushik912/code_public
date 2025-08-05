## Reverse Array in place
When reversing a subarray **in-place**, you're always using the **two-pointer technique**:

* One pointer starts at the **beginning** (`start`).
* One pointer starts at the **end** (`end`).
* You **swap** elements at `start` and `end`.
* Then move:

  * `start++`
  * `end--`

This continues **until `start >= end`**, which means you've reached (or passed) the **middle** of the subarray.

---

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

---

## Plus One
Given a non-negative number represented as a list of digits, add 1 to the number (increment the number represented by the digits). The digits are stored such that the most significant digit is first element of array.

🔹 **Flash Hint: Add 1 to Array of Digits**

* Start from last index, add `1` to current digit → `sum = digit + carry`.
* Set digit to `sum % 10`, update carry = `sum / 10`.
* Repeat till carry is `0` or start of array.
* If carry remains, insert it at front.

---

## Longest Consecutive Subsequence
Given an array arr[] of non-negative integers. Find the length of the longest sub-sequence such that elements in the subsequence are consecutive integers, the consecutive numbers can be in any order.


🔹 **Flash Hint: Longest Consecutive Subsequence**

1. Add all elements to a HashSet.
2. For each element `x`, if `x - 1` not in set → start counting.
3. Count by checking `x + 1, x + 2, ...` in set → increment length.
4. Track and update max length.




