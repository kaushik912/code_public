## Rearrange Array Alternately (with extra space)
Given an array of positive integers. Your task is to rearrange the array elements alternatively i.e. first element should be the max value, the second should be the min value, the third should be the second max, the fourth should be the second min, and so on.

🔹 **Flash Hint: Rearrange Array Alternately (with Extra Space)**

1. **Sort** the array.
2. Use two pointers: `i = 0` (start), `j = n - 1` (end).
3. Build a new array: pick from `arr[j]` (max), then `arr[i]` (min), alternate.
4. Copy new array back to original.

---

## Rearrange Array Alternately (without extra space)
Given an array of positive integers. Your task is to rearrange the array elements alternatively i.e. first element should be the max value, the second should be the min value, the third should be the second max, the fourth should be the second min, and so on.
Note: Modify the original array itself. Do it without using any extra space. You do not have to return anything.

### 📌 Flash Card: Rearrange Alternately (Max, Min, 2nd Max...)

🔹 **Step 1:** Sort the array.

🔹 **Step 2:** Initialize:
    `maxIdx = n - 1`, `minIdx = 0`
    `maxElem = arr[n - 1] + 1` (choose any number > max)

🔹 **Step 3:** For each index `i`:

* If `i % 2 == 0`: `arr[i] += (arr[maxIdx] % maxElem) * maxElem; maxIdx--;`
* Else: `arr[i] += (arr[minIdx] % maxElem) * maxElem; minIdx++;`

🔹 **Step 4:** Final pass:
    `arr[i] = arr[i] / maxElem;` for all `i`

✅ **In-place, O(1) space, O(n log n) time (due to sort)**

Great question! Let's break down the **logic behind encoding** and **why it works** in this rearrangement problem.


### 💡 **The Challenge**

We're trying to replace each element in-place, but:

* Once you overwrite a position with a new value, you **lose the original**.
* We need **both the original and new value** during computation.

---

### 🔐 **The Encoding Trick**

We use the formula:

```
arr[i] = arr[i] + (new_value % maxElem) * maxElem;
```

Why this works:

* We're **encoding two values** at each index:

  * The **original value** (needed for future reads),
  * The **target new value** (that should be at this index in the final array).
* `maxElem` is **greater than any array element**, so:

  * `arr[i] % maxElem` always retrieves the original value.
  * `arr[i] / maxElem` gives us the **new value** we encoded.

After processing all elements, we simply decode:

```
arr[i] = arr[i] / maxElem;
```

---

### ✅ **Example**

Let's say original array = `[1, 2, 3, 4, 5, 6]` (sorted),
Target rearrangement = `[6, 1, 5, 2, 4, 3]`

1. Set `maxElem = 7` (greater than any element).
2. Start encoding:

   * `arr[0] = 1 + (6 % 7) * 7 = 1 + 6 * 7 = 43`
   * `arr[1] = 2 + (1 % 7) * 7 = 2 + 1 * 7 = 9`
   * ...
3. Now, after all are encoded, decode:

   * `arr[0] = 43 / 7 = 6`
   * `arr[1] = 9 / 7 = 1`
   * ...

Result: `[6, 1, 5, 2, 4, 3]`

---

### 🧠 Key Insight

This works because:

* We're using the division and modulus relationship:

  * Any number `N` encoded as `a + b * maxElem` can be broken into:

    * `N % maxElem = a` (original value),
    * `N / maxElem = b` (new rearranged value).

---
