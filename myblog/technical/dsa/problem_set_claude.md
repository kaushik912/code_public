Here's an expanded list, weighted heavily toward **arrays and strings**, split by difficulty. I've kept the other patterns lighter since you asked to prioritize these two.

---

## ARRAYS

### Easy
- Two Sum
- Contains Duplicate
- Best Time to Buy and Sell Stock
- Maximum Subarray (Kadane's) ⭐
- Move Zeroes
- Plus One
- Remove Duplicates from Sorted Array
- Merge Sorted Array
- Majority Element (Boyer-Moore)
- Single Number (XOR trick)
- Running Sum of 1d Array
- Find Pivot Index

### Medium
- 3Sum ⭐
- Product of Array Except Self ⭐
- Container With Most Water
- Two Sum II (sorted, two-pointer)
- Sort Colors (Dutch National Flag) ⭐
- Subarray Sum Equals K ⭐ (prefix sum + hashmap)
- Next Permutation
- Rotate Array
- Set Matrix Zeroes
- Spiral Matrix
- Rotate Image (matrix in-place)
- Find All Duplicates in an Array
- Maximum Product Subarray
- Longest Consecutive Sequence ⭐
- Merge Intervals ⭐
- Insert Interval
- Non-overlapping Intervals
- Jump Game
- Gas Station
- Increasing Triplet Subsequence

### Hard
- Trapping Rain Water ⭐
- First Missing Positive
- Median of Two Sorted Arrays
- Largest Rectangle in Histogram
- Sliding Window Maximum
- Max Value of Equation

---

## STRINGS

### Easy
- Valid Anagram
- Valid Palindrome ⭐
- Longest Common Prefix
- Roman to Integer
- Implement strStr() / Index of First Occurrence
- Reverse String
- Reverse Words in a String III
- First Unique Character in a String
- Is Subsequence
- Length of Last Word

### Medium
- Longest Substring Without Repeating Characters ⭐
- Longest Palindromic Substring ⭐ (expand-around-center)
- Group Anagrams ⭐
- Longest Repeating Character Replacement
- Palindromic Substrings (count)
- String to Integer (atoi)
- Generate Parentheses (backtracking)
- Letter Combinations of a Phone Number
- Encode and Decode Strings
- Find All Anagrams in a String (sliding window) ⭐
- Permutation in String
- Zigzag Conversion
- Decode String (stack)
- Multiply Strings
- Reorganize String

### Hard
- Minimum Window Substring ⭐
- Longest Valid Parentheses
- Valid Number
- Text Justification
- Substring with Concatenation of All Words
- Edit Distance (DP — string + DP crossover, very common) ⭐

---

## SLIDING WINDOW & TWO POINTERS (the array/string workhorses)

These two techniques cover a huge fraction of array/string mediums — drill them until recognition is instant.

**Two Pointers pattern:** Valid Palindrome, 3Sum, Container With Most Water, Trapping Rain Water, Sort Colors, Remove Duplicates, Two Sum II

**Sliding Window pattern:** Longest Substring Without Repeating, Minimum Window Substring, Longest Repeating Character Replacement, Find All Anagrams, Permutation in String, Max Consecutive Ones III, Fruit Into Baskets, Subarray Product Less Than K

**Prefix Sum pattern:** Subarray Sum Equals K, Product of Array Except Self, Running Sum, Find Pivot Index, Range Sum Query

---

## Lighter coverage (still worth touching)

**Hashing:** Two Sum, Group Anagrams, Longest Consecutive Sequence, Top K Frequent Elements
**Stack (string-heavy):** Valid Parentheses, Decode String, Min Stack, Daily Temperatures
**Binary Search:** Search in Rotated Sorted Array, Find Min in Rotated, Koko Eating Bananas, Median of Two Sorted Arrays
**DP (string overlap):** Longest Common Subsequence, Edit Distance, Word Break, Longest Palindromic Substring

---

## Suggested re-weighting of your week

Since you're prioritizing arrays/strings:

| Day | Focus |
|---|---|
| 1 | Array Easy + Two Pointers |
| 2 | Array Medium (prefix sum, intervals) |
| 3 | Sliding Window (arrays + strings) ⭐ |
| 4 | String Easy + Medium |
| 5 | String Medium/Hard + Stack |
| 6 | Array/String Hard + Binary Search |
| 7 | Mock interviews + review ⭐ list |

---

### The 3 patterns that give the best ROI for array/string interviews
1. **Two Pointers** — collapses O(n²) to O(n)
2. **Sliding Window** — every "longest/shortest substring/subarray" question
3. **Prefix Sum + HashMap** — every "subarray sums to K" variant

Master these three and you'll recognize 70%+ of array/string mediums on sight.

Want me to drop this into a trackable markdown checklist file (with checkboxes and a spot to note the pattern for each), so you can mark progress as you go this week?
