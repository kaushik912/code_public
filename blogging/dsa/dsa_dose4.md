## Longest substring without repeating characters

Given a string `s`, find the length of the **longest substring** that does not contain any repeating characters.

* A **substring** is a contiguous sequence of characters within the string.
* The goal is to determine the maximum possible length of such a substring.

**Example:**

* Input: `"abcabcbb"`

* Output: `3` (The answer is `"abc"`)

* Input: `"bbbbb"`

* Output: `1` (The answer is `"b"`)

* Input: `"pwwkew"`

* Output: `3` (The answer is `"wke"`)


### Solution Hint

```
for right in [0..n):
    if s[right] in map:
        left = max(left, map[s[right]] + 1)
    map[s[right]] = right
    maxLen = max(maxLen, right - left + 1)
```

✅ The key trick is exactly that `left = Math.max(left, lastSeen + 1)`. This prevents `left` from ever moving backward when duplicates occur.

---



