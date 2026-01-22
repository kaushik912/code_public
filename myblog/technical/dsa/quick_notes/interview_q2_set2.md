# 🎯 FAANG + Product Companies Coding Interview Questions
## Topic-Wise Guide (Easy → Medium)

---

## 📊 **1. ARRAYS**

### Easy (Build Confidence) ⭐
1. **Two Sum** - Find two numbers that add up to target
   - Companies: Google, Amazon, Microsoft, VMware
   - Pattern: Hash table lookup
   
2. **Best Time to Buy and Sell Stock** - Find max profit from stock prices
   - Companies: Amazon, Facebook, Bloomberg
   - Pattern: Single pass tracking
   
3. **Contains Duplicate** - Check if array has duplicates
   - Companies: Amazon, Adobe, Yahoo
   - Pattern: Hash set
   
4. **Maximum Subarray** (Kadane's Algorithm) - Find contiguous subarray with max sum
   - Companies: Microsoft, LinkedIn, Amazon
   - Pattern: Dynamic programming
   
5. **Move Zeroes** - Move all zeros to end maintaining order
   - Companies: Facebook, Bloomberg
   - Pattern: Two pointers
   
6. **Plus One** - Add one to number represented as array
   - Companies: Google, Amazon
   - Pattern: Array manipulation

### Medium (Flex Your Brain) 💪
1. **Product of Array Except Self** - Calculate products without division
   - Companies: Amazon, Microsoft, Apple, Atlassian
   - Pattern: Prefix/suffix products
   
2. **Maximum Product Subarray** - Find subarray with maximum product
   - Companies: LinkedIn, Microsoft
   - Pattern: Dynamic programming with min/max tracking
   
3. **3Sum** - Find triplets that sum to zero
   - Companies: Facebook, Amazon, VMware, ServiceNow
   - Pattern: Two pointers + sorting
   
4. **Container With Most Water** - Find container with max water
   - Companies: Amazon, Google, Bloomberg
   - Pattern: Two pointers (greedy)
   
5. **Search in Rotated Sorted Array** - Binary search in rotated array
   - Companies: Microsoft, Amazon, VMware, ServiceNow
   - Pattern: Modified binary search
   
6. **Find Minimum in Rotated Sorted Array** - Find minimum in rotated array
   - Companies: Microsoft, Amazon
   - Pattern: Binary search
   
7. **Subarray Sum Equals K** - Count subarrays with sum K
   - Companies: Facebook, Google
   - Pattern: Prefix sum + hash map
   
8. **Degree of an Array** - Find smallest subarray with same degree as array
   - Companies: VMware
   - Pattern: Hash map tracking
   
9. **Merge Intervals** - Merge overlapping intervals
   - Companies: Facebook, Google, Bloomberg, Atlassian
   - Pattern: Sorting + merging
   
10. **Insert Interval** - Insert interval into sorted intervals
    - Companies: Google, LinkedIn, Facebook
    - Pattern: Merge intervals variant

11. **Replace Space with %20** - Replace spaces in string with %20
    - Companies: Amazon
    - Pattern: String manipulation in-place

12. **Majority Element** (Boyer-Moore) - Find element appearing more than n/2 times
    - Companies: Amazon
    - Pattern: Boyer-Moore majority vote algorithm

13. **String Rotation** - Check if one string is rotation of another
    - Companies: PayPal
    - Pattern: String concatenation + substring search

14. **Plus One Matrix** - Find highest plus(+) size of 1s in matrix
    - Companies: Amazon
    - Pattern: Dynamic programming on matrix

---

## 🗝️ **2. HASHING (Hash Tables / Hash Maps / Sets)**

### Easy (Build Confidence) ⭐
1. **Valid Anagram** - Check if two strings are anagrams
   - Companies: Amazon, Uber, Bloomberg
   - Pattern: Character frequency counting
   
2. **First Unique Character in String** - Find first non-repeating character
   - Companies: Amazon, Microsoft, Google
   - Pattern: Hash map frequency
   
3. **Intersection of Two Arrays** - Find common elements
   - Companies: Facebook, Amazon
   - Pattern: Hash set intersection
   
4. **Happy Number** - Determine if number is happy
   - Companies: Google, Airbnb
   - Pattern: Hash set cycle detection
   
5. **Isomorphic Strings** - Check if two strings are isomorphic
   - Companies: LinkedIn, Google
   - Pattern: Two hash maps

### Medium (Flex Your Brain) 💪
1. **Group Anagrams** - Group strings that are anagrams
   - Companies: Amazon, Facebook, Uber, Atlassian
   - Pattern: Hash map with sorted string as key
   
2. **Top K Frequent Elements** - Find k most frequent elements
   - Companies: Amazon, Yelp, ServiceNow
   - Pattern: Hash map + heap/bucket sort
   
3. **Longest Consecutive Sequence** - Find longest sequence in unsorted array
   - Companies: Google, Facebook
   - Pattern: Hash set for O(1) lookups
   
4. **Subarray Sum Equals K** - Count subarrays with sum K
   - Companies: Facebook, Google, Amazon
   - Pattern: Prefix sum + hash map
   
5. **LRU Cache** - Implement Least Recently Used cache
   - Companies: Amazon, Google, Microsoft, VMware, Atlassian
   - Pattern: Hash map + doubly linked list
   
6. **Design HashMap** - Implement a hash map from scratch
   - Companies: Oracle, ServiceNow
   - Pattern: Array of buckets (chaining/open addressing)
   
7. **Encode and Decode Strings** - Serialize/deserialize string array
   - Companies: Google, Facebook
   - Pattern: Custom encoding scheme
   
8. **Longest Substring Without Repeating Characters** - Find longest unique substring
   - Companies: Amazon, Adobe, Bloomberg
   - Pattern: Sliding window + hash map

---

## 🔄 **3. TWO POINTERS**

### Easy (Build Confidence) ⭐
1. **Valid Palindrome** - Check if string is palindrome
   - Companies: Microsoft, Facebook, VMware
   - Pattern: Two pointers from both ends
   
2. **Remove Duplicates from Sorted Array** - Remove duplicates in-place
   - Companies: Facebook, Amazon
   - Pattern: Slow and fast pointer
   
3. **Merge Sorted Array** - Merge two sorted arrays in-place
   - Companies: Facebook, Microsoft, Bloomberg
   - Pattern: Three pointers from end

### Medium (Flex Your Brain) 💪
1. **3Sum** - Find triplets that sum to zero
   - Companies: Facebook, Amazon, ServiceNow
   - Pattern: Sorting + two pointers
   
2. **Container With Most Water** - Find container with max water
   - Companies: Amazon, Google, VMware
   - Pattern: Greedy two pointers
   
3. **Trapping Rain Water** - Calculate trapped rainwater
   - Companies: Amazon, Google, Microsoft, ServiceNow
   - Pattern: Two pointers or DP
   
4. **Sort Colors** (Dutch National Flag) - Sort array with 0s, 1s, 2s
   - Companies: Microsoft, Facebook
   - Pattern: Three-way partitioning
   
5. **Remove Nth Node From End of List** - Remove nth node from end
   - Companies: Amazon, Microsoft
   - Pattern: Fast and slow pointers

6. **Is Subsequence** - Check if string is subsequence of another
   - Companies: Microsoft
   - Pattern: Two pointers matching characters

---

## 🪟 **4. SLIDING WINDOW**

### Easy (Build Confidence) ⭐
1. **Maximum Average Subarray I** - Find max average of k elements
   - Companies: Amazon, Google
   - Pattern: Fixed window
   
2. **Best Time to Buy and Sell Stock** - Find max profit
   - Companies: Amazon, Facebook, Bloomberg
   - Pattern: Track minimum and maximum

### Medium (Flex Your Brain) 💪
1. **Longest Substring Without Repeating Characters** - Find longest unique substring
   - Companies: Amazon, Adobe, Bloomberg, Atlassian
   - Pattern: Dynamic window + hash map
   
2. **Longest Repeating Character Replacement** - Replace k chars for longest substring
   - Companies: Google, Amazon
   - Pattern: Window with character frequency
   
3. **Minimum Window Substring** - Find smallest window containing all chars
   - Companies: Facebook, Uber, LinkedIn
   - Pattern: Two pointers + hash map
   
4. **Permutation in String** - Check if one string is permutation of another
   - Companies: Microsoft, Amazon
   - Pattern: Fixed window + character count
   
5. **Sliding Window Maximum** - Maximum in each window of size k
   - Companies: Amazon, Google, ServiceNow
   - Pattern: Deque (monotonic queue)

---

## 📚 **5. STACK**

### Easy (Build Confidence) ⭐
1. **Valid Parentheses** - Check if brackets are balanced
   - Companies: Amazon, Google, Microsoft, Bloomberg
   - Pattern: Stack for matching pairs
   
2. **Min Stack** - Stack with O(1) min operation
   - Companies: Amazon, Google, Bloomberg
   - Pattern: Auxiliary stack or single stack with pairs
   
3. **Implement Stack using Queues** - Design stack using queue operations
   - Companies: ServiceNow, Bloomberg
   - Pattern: Two queues or one queue

### Medium (Flex Your Brain) 💪
1. **Daily Temperatures** - Days until warmer temperature
   - Companies: Amazon, Google
   - Pattern: Monotonic stack
   
2. **Evaluate Reverse Polish Notation** - Calculate RPN expression
   - Companies: LinkedIn, Amazon
   - Pattern: Stack for operands
   
3. **Generate Parentheses** - Generate all valid parentheses combinations
   - Companies: Google, Facebook
   - Pattern: Backtracking with stack validation
   
4. **Decode String** - Decode encoded string with brackets
   - Companies: Google, Amazon
   - Pattern: Stack for nested structures
   
5. **Basic Calculator II** - Implement calculator with +, -, *, /
   - Companies: Amazon, Facebook, Atlassian
   - Pattern: Stack for operator precedence

6. **Next Greater Element** - Find next greater element in array
   - Companies: Amazon
   - Pattern: Monotonic stack

7. **Mid Element in Stack** - Find middle element in O(1) time
   - Companies: Amazon
   - Pattern: Auxiliary stack or modified stack implementation

---

## 🔍 **6. BINARY SEARCH**

### Easy (Build Confidence) ⭐
1. **Binary Search** - Standard binary search
   - Companies: All companies
   - Pattern: Basic divide and conquer
   
2. **Search Insert Position** - Find insert position in sorted array
   - Companies: Amazon, LinkedIn
   - Pattern: Binary search variant
   
3. **First Bad Version** - Find first bad version with API
   - Companies: Facebook, Amazon
   - Pattern: Binary search on unknown range

### Medium (Flex Your Brain) 💪
1. **Search in Rotated Sorted Array** - Binary search in rotated array
   - Companies: Microsoft, Amazon, VMware, ServiceNow
   - Pattern: Modified binary search with pivot
   
2. **Find Minimum in Rotated Sorted Array** - Find minimum in rotated array
   - Companies: Microsoft, Amazon, VMware
   - Pattern: Binary search for minimum
   
3. **Search a 2D Matrix** - Search in row-column sorted matrix
   - Companies: Amazon, Microsoft
   - Pattern: Treat as 1D array or binary search twice
   
4. **Find Peak Element** - Find any peak in array
   - Companies: Google, Microsoft, VMware
   - Pattern: Binary search on unsorted array
   
5. **Time Based Key-Value Store** - Design time-based data structure
   - Companies: Amazon, Google
   - Pattern: Binary search on timestamps
   
6. **Koko Eating Bananas** - Find minimum eating speed
   - Companies: Google, Facebook
   - Pattern: Binary search on answer space

7. **Count Occurrences in Sorted Array** - Count frequency of target in sorted array
   - Companies: Amazon
   - Pattern: Binary search for first and last occurrence

---

## 🔗 **7. LINKED LISTS**

### Easy (Build Confidence) ⭐
1. **Reverse Linked List** - Reverse a singly linked list
   - Companies: Amazon, Microsoft, Facebook, VMware
   - Pattern: Iterative or recursive reversal
   
2. **Merge Two Sorted Lists** - Merge two sorted lists
   - Companies: Amazon, Microsoft, Apple
   - Pattern: Two pointers merge
   
3. **Linked List Cycle** - Detect cycle in linked list
   - Companies: Amazon, Microsoft, Yahoo
   - Pattern: Floyd's cycle detection
   
4. **Palindrome Linked List** - Check if linked list is palindrome
   - Companies: Facebook, Amazon
   - Pattern: Fast/slow pointer + reverse
   
5. **Convert Binary Number in Linked List to Integer** - Binary to decimal
   - Companies: ServiceNow
   - Pattern: Traverse and accumulate

### Medium (Flex Your Brain) 💪
1. **Add Two Numbers** - Add numbers represented as linked lists
   - Companies: Amazon, Microsoft, Bloomberg
   - Pattern: Simulate addition with carry
   
2. **Reorder List** - Reorder list in specific pattern
   - Companies: Amazon, Facebook
   - Pattern: Find middle + reverse + merge
   
3. **Remove Nth Node From End** - Remove nth node from end
   - Companies: Amazon, Microsoft, Facebook
   - Pattern: Two pointers (fast/slow)
   
4. **Copy List with Random Pointer** - Deep copy list with random pointers
   - Companies: Amazon, Microsoft, Bloomberg
   - Pattern: Hash map or interweave nodes
   
5. **LRU Cache** - Implement LRU cache
   - Companies: Amazon, Microsoft, Facebook, Atlassian
   - Pattern: Hash map + doubly linked list
   
6. **Merge K Sorted Lists** - Merge k sorted linked lists
   - Companies: Amazon, Google, Uber, VMware
   - Pattern: Min heap or divide and conquer
   
7. **Intersection of Two Linked Lists** - Find intersection point
   - Companies: Amazon, Microsoft, Bloomberg
   - Pattern: Two pointers with length difference

8. **Delete Node Given Only Pointer** - Delete node when only given pointer to that node
   - Companies: Citibank
   - Pattern: Copy next node's data and delete next

9. **Detect Common Node in Two Lists** - Check if two linked lists have a common node
   - Companies: Microsoft
   - Pattern: Hash set or two pointers technique

---

## 🌲 **8. TREES**

### Easy (Build Confidence) ⭐
1. **Invert Binary Tree** - Flip tree left-right
   - Companies: Google, Amazon
   - Pattern: DFS or BFS swap
   
2. **Maximum Depth of Binary Tree** - Find tree height
   - Companies: LinkedIn, Uber
   - Pattern: DFS or BFS
   
3. **Same Tree** - Check if two trees are identical
   - Companies: Bloomberg, Amazon
   - Pattern: Recursive comparison
   
4. **Subtree of Another Tree** - Check if tree is subtree
   - Companies: Amazon, Facebook, ServiceNow
   - Pattern: Tree traversal + comparison
   
5. **Symmetric Tree** - Check if tree is mirror of itself
   - Companies: Microsoft, LinkedIn
   - Pattern: Recursive mirror check
   
6. **Diameter of Binary Tree** - Find longest path between any two nodes
   - Companies: Google, Facebook
   - Pattern: DFS with height tracking

### Medium (Flex Your Brain) 💪
1. **Validate Binary Search Tree** - Check if valid BST
   - Companies: Amazon, Microsoft, Facebook, VMware
   - Pattern: In-order traversal or range validation
   
2. **Binary Tree Level Order Traversal** - Level-by-level traversal
   - Companies: Amazon, Microsoft, LinkedIn, Atlassian
   - Pattern: BFS with queue
   
3. **Lowest Common Ancestor of BST** - Find LCA in BST
   - Companies: Amazon, Microsoft, Facebook, VMware
   - Pattern: BST property exploitation
   
4. **Kth Smallest Element in BST** - Find kth smallest in BST
   - Companies: Google, Uber, Bloomberg
   - Pattern: In-order traversal
   
5. **Construct Binary Tree from Preorder and Inorder** - Build tree from traversals
   - Companies: Microsoft, Amazon, Bloomberg
   - Pattern: Recursive construction with indices
   
6. **Binary Tree Right Side View** - Rightmost nodes at each level
   - Companies: Amazon, Facebook
   - Pattern: BFS or DFS with level tracking
   
7. **Count Good Nodes in Binary Tree** - Count nodes ≥ ancestors
   - Companies: Amazon, Microsoft
   - Pattern: DFS with max value tracking
   
8. **Path Sum II** - Find all root-to-leaf paths with target sum
   - Companies: Facebook, Amazon
   - Pattern: DFS backtracking
   
9. **Populating Next Right Pointers** - Connect nodes at same level
   - Companies: Microsoft, Facebook
   - Pattern: BFS or constant space solution

10. **Binary Tree Top View** - Print top view of binary tree
    - Companies: Amazon
    - Pattern: Level order traversal with horizontal distance

11. **Binary Tree Diagonal View** - Print diagonal view of binary tree
    - Companies: Amazon
    - Pattern: DFS with diagonal distance tracking

12. **Binary Tree Left View** - Print leftmost nodes at each level
    - Companies: VMware
    - Pattern: Level order traversal or DFS with level tracking

13. **Recover Binary Search Tree** - Fix BST with two swapped nodes
    - Companies: Amazon
    - Pattern: In-order traversal to find swapped nodes

### Hard (Challenge) 🔥
1. **Binary Tree Maximum Path Sum** - Find max path sum
   - Companies: Amazon, Facebook, Google
   - Pattern: DFS with global max
   
2. **Serialize and Deserialize Binary Tree** - Convert tree to/from string
   - Companies: Amazon, Google, LinkedIn
   - Pattern: Pre-order/level-order encoding

---

## 🔺 **9. HEAP / PRIORITY QUEUE**

### Easy (Build Confidence) ⭐
1. **Kth Largest Element in Stream** - Maintain kth largest
   - Companies: Amazon, Facebook
   - Pattern: Min heap of size k
   
2. **Last Stone Weight** - Simulate stone smashing
   - Companies: Amazon
   - Pattern: Max heap

### Medium (Flex Your Brain) 💪
1. **Top K Frequent Elements** - Find k most frequent elements
   - Companies: Amazon, Yelp, ServiceNow
   - Pattern: Hash map + min heap
   
2. **K Closest Points to Origin** - Find k nearest points
   - Companies: Amazon, Facebook, Asana
   - Pattern: Max heap or quickselect
   
3. **Find Median from Data Stream** - Maintain running median
   - Companies: Google, Amazon, Microsoft
   - Pattern: Two heaps (max + min)
   
4. **Task Scheduler** - Schedule tasks with cooldown
   - Companies: Facebook, Amazon
   - Pattern: Greedy + max heap
   
5. **Merge K Sorted Lists** - Merge k sorted linked lists
   - Companies: Amazon, Google, Uber, VMware
   - Pattern: Min heap with k elements

6. **K Closest Stars to Earth** - Find k nearest stars from given distances
   - Companies: Amazon
   - Pattern: Max heap of size k or quickselect

---

## 🔙 **10. BACKTRACKING**

### Medium (Flex Your Brain) 💪
1. **Subsets** - Generate all subsets
   - Companies: Amazon, Facebook, Bloomberg
   - Pattern: Decision tree exploration
   
2. **Permutations** - Generate all permutations
   - Companies: LinkedIn, Microsoft
   - Pattern: Backtracking with used array
   
3. **Combination Sum** - Find combinations that sum to target
   - Companies: Amazon, Airbnb, Snapchat
   - Pattern: Backtracking with index
   
4. **Word Search** - Find word in 2D grid
   - Companies: Microsoft, Amazon, Bloomberg
   - Pattern: DFS backtracking on grid
   
5. **Letter Combinations of Phone Number** - Generate letter combos
   - Companies: Amazon, Google, Uber
   - Pattern: Backtracking with mapping
   
6. **Palindrome Partitioning** - Partition string into palindromes
   - Companies: Amazon, Google
   - Pattern: Backtracking + palindrome check
   
7. **Generate Parentheses** - Generate all valid parentheses
   - Companies: Google, Facebook, Uber
   - Pattern: Backtracking with constraints

---

## 🌐 **11. GRAPHS**

### Medium (Flex Your Brain) 💪
1. **Number of Islands** - Count islands in grid
   - Companies: Amazon, Facebook, Google, ServiceNow, Atlassian
   - Pattern: DFS/BFS on grid
   
2. **Clone Graph** - Deep copy undirected graph
   - Companies: Amazon, Google, Facebook
   - Pattern: DFS/BFS with hash map
   
3. **Course Schedule** - Detect cycle in directed graph (topological sort check)
   - Companies: Amazon, Microsoft, Atlassian
   - Pattern: Topological sort / DFS cycle detection
   
4. **Course Schedule II** - Return topological order
   - Companies: Amazon, Microsoft, Facebook
   - Pattern: Topological sort with Kahn's algorithm or DFS
   
5. **Pacific Atlantic Water Flow** - Find cells reaching both oceans
   - Companies: Google, Amazon
   - Pattern: Multi-source BFS/DFS
   
6. **Graph Valid Tree** - Check if graph is valid tree
   - Companies: Google, Facebook, Atlassian
   - Pattern: Union-find or DFS cycle detection
   
7. **Number of Connected Components** - Count connected components
   - Companies: Amazon, Facebook
   - Pattern: Union-find or DFS/BFS
   
8. **Rotting Oranges** - BFS simulation problem
   - Companies: Amazon, Bloomberg
   - Pattern: Multi-source BFS

### Hard (Challenge) 🔥
1. **Word Ladder** - Find shortest transformation sequence
   - Companies: Amazon, Facebook, LinkedIn
   - Pattern: BFS with word graph

---

## 💎 **12. DYNAMIC PROGRAMMING**

### Easy (Build Confidence) ⭐
1. **Climbing Stairs** - Count ways to climb stairs
   - Companies: Amazon, Adobe, Apple
   - Pattern: Fibonacci-style DP
   
2. **House Robber** - Rob houses without adjacent ones
   - Companies: LinkedIn, Airbnb
   - Pattern: DP with two states
   
3. **Min Cost Climbing Stairs** - Minimum cost to reach top
   - Companies: Amazon
   - Pattern: DP with cost tracking

### Medium (Flex Your Brain) 💪
1. **Coin Change** - Minimum coins for amount
   - Companies: Amazon, Atlassian
   - Pattern: Unbounded knapsack
   
2. **Longest Increasing Subsequence** - Find LIS length
   - Companies: Microsoft, Amazon
   - Pattern: DP with patience sorting
   
3. **Word Break** - Check if string can be segmented
   - Companies: Google, Facebook, Amazon
   - Pattern: DP with word dictionary
   
4. **Unique Paths** - Count paths in grid
   - Companies: Google, Bloomberg, Atlassian
   - Pattern: 2D DP grid
   
5. **Jump Game** - Can reach last index
   - Companies: Amazon, Microsoft
   - Pattern: Greedy or DP
   
6. **Decode Ways** - Count ways to decode string
   - Companies: Facebook, Google, Uber
   - Pattern: Fibonacci-style with constraints
   
7. **Maximum Product Subarray** - Find max product subarray
   - Companies: LinkedIn, Microsoft
   - Pattern: DP tracking min and max
   
8. **House Robber II** - Rob circular houses
   - Companies: Microsoft, Amazon
   - Pattern: Two passes of House Robber I
   
9. **Longest Palindromic Substring** - Find longest palindrome
   - Companies: Amazon, Microsoft, ServiceNow
   - Pattern: Expand around center or DP
   
10. **Palindromic Substrings** - Count palindromic substrings
    - Companies: Facebook, LinkedIn
    - Pattern: Expand around center or DP
    
11. **Maximum Path Sum in Matrix** - Find max sum path from top to bottom
    - Companies: ServiceNow
    - Pattern: 2D DP bottom-up or top-down

12. **Best Time to Buy and Sell Stock with K Transactions** - Max profit with at most k transactions
    - Companies: Amazon
    - Pattern: 2D DP with state transitions

### Hard (Challenge) 🔥
1. **Edit Distance** - Minimum operations to convert strings
   - Companies: Google, Amazon
   - Pattern: 2D DP string matching
   
2. **Regular Expression Matching** - Implement regex matcher
   - Companies: Google, Facebook
   - Pattern: 2D DP with wildcard handling
   
3. **Rod Cutting Problem** - Maximize profit by cutting rod
   - Companies: ServiceNow
   - Pattern: Unbounded knapsack variant

---

## ⏱️ **13. INTERVALS**

### Easy (Build Confidence) ⭐
1. **Meeting Rooms** - Check if person can attend all meetings
   - Companies: Facebook, Bloomberg
   - Pattern: Sort and check overlaps

### Medium (Flex Your Brain) 💪
1. **Merge Intervals** - Merge overlapping intervals
   - Companies: Facebook, Google, Bloomberg, Atlassian
   - Pattern: Sort and merge
   
2. **Insert Interval** - Insert interval into sorted intervals
   - Companies: Google, LinkedIn, Facebook
   - Pattern: Three-part merge
   
3. **Non-overlapping Intervals** - Remove min intervals for non-overlap
   - Companies: Amazon, Facebook
   - Pattern: Greedy with end time sorting
   
4. **Meeting Rooms II** - Find min conference rooms needed
   - Companies: Google, Amazon, Facebook
   - Pattern: Event sorting or min heap
   
5. **Minimum Number of Arrows to Burst Balloons** - Min arrows for bursting
   - Companies: Microsoft, Amazon
   - Pattern: Greedy interval scheduling

---

## 🔢 **14. BIT MANIPULATION**

### Easy (Build Confidence) ⭐
1. **Number of 1 Bits** (Hamming Weight) - Count set bits
   - Companies: Apple, Amazon
   - Pattern: Brian Kernighan's algorithm
   
2. **Counting Bits** - Count bits for 0 to n
   - Companies: Amazon, Google
   - Pattern: DP using i & (i-1)
   
3. **Reverse Bits** - Reverse bits of integer
   - Companies: Apple, Airbnb
   - Pattern: Bit manipulation with mask
   
4. **Missing Number** - Find missing number in array
   - Companies: Amazon, Microsoft
   - Pattern: XOR or sum formula
   
5. **Single Number** - Find number appearing once
   - Companies: Amazon, Airbnb, Palantir
   - Pattern: XOR

### Medium (Flex Your Brain) 💪
1. **Sum of Two Integers** - Add without + or - operator
   - Companies: Amazon
   - Pattern: Bit manipulation with carry
   
2. **Single Number II** - Find single number when others appear 3 times
   - Companies: Amazon, Google
   - Pattern: Bit counting or state machine
   
3. **Single Number III** - Find two single numbers
   - Companies: Amazon
   - Pattern: XOR with partitioning

---

## 📐 **15. MATH & GEOMETRY**

### Easy (Build Confidence) ⭐
1. **Happy Number** - Check if number is happy
   - Companies: Google, Airbnb, Uber
   - Pattern: Hash set cycle detection
   
2. **Plus One** - Add one to number as array
   - Companies: Google, Amazon
   - Pattern: Array manipulation with carry
   
3. **Palindrome Number** - Check if number is palindrome
   - Companies: Amazon, Facebook
   - Pattern: Reverse or two pointers

### Medium (Flex Your Brain) 💪
1. **Rotate Image** - Rotate matrix 90 degrees
   - Companies: Amazon, Microsoft, Apple
   - Pattern: Transpose + reverse
   
2. **Spiral Matrix** - Return spiral order of matrix
   - Companies: Amazon, Microsoft, ServiceNow
   - Pattern: Four-pointer boundary tracking
   
3. **Set Matrix Zeroes** - Set rows/cols to zero
   - Companies: Amazon, Microsoft, Microsoft
   - Pattern: In-place marking
   
4. **Pow(x, n)** - Calculate power efficiently
   - Companies: Google, Facebook, LinkedIn
   - Pattern: Fast exponentiation (divide and conquer)
   
5. **Detect Squares** - Count squares from points
   - Companies: Google, Amazon
   - Pattern: Hash map with geometry

6. **Palindrome Number (No Reverse)** - Check palindrome using mod/length only
   - Companies: Oracle
   - Pattern: Compare digits from both ends using math

7. **Producer-Consumer with Threads** - Synchronize even/odd number printing
   - Companies: VMware, Citibank
   - Pattern: Thread synchronization with semaphores/locks

---

## 🏢 **PRODUCT COMPANIES SPECIFIC QUESTIONS**

### VMware Focus Areas 🟢
**Infrastructure & System-Level Problems:**
- Efficient graph, tree, heap traversal and mutation
- Lock-free programming, thread safety, CPU/memory optimization
- Cache invalidation strategies
- Distributed system debugging
- K-sorted lists merging
- Degree of an Array
- Valid BST variations

### Atlassian Focus Areas 🔵
**Collaboration Tools & Clean Code:**
- Rate Limiter design (Fixed Window, Sliding Window)
- Multi-threading with ConcurrentHashMap
- File collection size aggregation (nested collections)
- Web scraper design
- Rank Team by Votes
- Database design for Confluence (tags, likes, views)
- Focus on production-ready, clean code
- String manipulation and array problems

### ServiceNow Focus Areas 🟣
**Enterprise Platform & Integration:**
- Binary to decimal conversion
- Maximum path sum in matrix
- Sliding Window Maximum
- N max sums from two sorted arrays (Ai + Bj)
- Survey system design
- Rate limiting system
- Producer-Consumer implementation
- Stack using Queues
- Currency converter implementation
- Database optimization
- 3Sum variants
- Builder and Factory design patterns

### Common Patterns Across All Product Companies:
1. **System Design** (30-40% of interviews)
   - Rate limiters
   - Cache systems (LRU, LFU)
   - Distributed systems
   - Database design
   
2. **Clean Code Emphasis**
   - Production-ready code
   - Error handling
   - Edge cases
   - Code organization and modularity
   
3. **Concurrency** (Important for all)
   - Thread safety
   - Synchronization
   - Lock-free data structures
   
4. **Real-world Scenarios**
   - File systems
   - Data aggregation
   - Multi-tenancy
   - API design

---

## 📋 **STUDY PLAN**

### Week 1-2: Foundation (Easy Problems)
**Focus:** Arrays, Hashing, Two Pointers, Strings
- **Goal:** 3-4 easy problems/day
- **Companies:** Start with FAANG easy problems
- **Practice:** LeetCode, HackerRank
- Build muscle memory for basic patterns

### Week 3-4: Core Structures (Medium Problems)
**Focus:** Stacks, Queues, Linked Lists, Trees
- **Goal:** 2-3 medium problems/day
- **Companies:** Mix FAANG + Product companies
- Understand tree traversals (BFS, DFS)
- Master stack/queue applications

### Week 5-6: Advanced Topics (Medium-Hard)
**Focus:** Graphs, Dynamic Programming, Heaps
- **Goal:** 2 medium or 1 hard problem/day
- **Companies:** Product company specific patterns
- Graph traversals and topological sort
- DP patterns recognition

### Week 7-8: System Design + Integration
**Focus:** System design + Mixed difficulty
- **Goal:** 1-2 coding + 1 system design/day
- **Companies:** VMware, Atlassian, ServiceNow focus
- Design rate limiters, caches, distributed systems
- Practice clean code and multi-threading

### Week 9-10: Mock Interviews
**Focus:** Timed practice + Full interview simulation
- **Goal:** 2-3 full mock interviews/week
- **Companies:** Target company specific prep
- 45 minutes per coding problem
- Explain approach before coding
- Handle follow-up questions

---

## 💡 **PRO TIPS FOR PRODUCT COMPANIES**

### For VMware:
1. **Focus on systems-level thinking**
2. Study open-source tools (Open vSwitch, Harbor, Velero)
3. Practice infrastructure optimization problems
4. Be ready for C++ and networking questions
5. Understand virtualization concepts

### For Atlassian:
1. **Emphasize clean, production-ready code**
2. Study their values framework (look up official documentation)
3. Practice explaining trade-offs between approaches
4. Strong focus on scalability discussions
5. Prepare for multi-threading scenarios

### For ServiceNow:
1. **Mix of DSA + Design patterns**
2. Practice OOP principles thoroughly
3. Database design and optimization
4. Event-driven architecture concepts
5. Prepare for behavioral questions with STAR method

### General Product Company Tips:
1. **Code Quality > Speed**
   - Take time to write clean, readable code
   - Use meaningful variable names
   - Add comments for complex logic

2. **Communication is Key**
   - Think out loud
   - Explain your approach before coding
   - Discuss trade-offs

3. **Ask Clarifying Questions**
   - Confirm requirements
   - Discuss edge cases
   - Understand scale requirements

4. **Follow-up Handling**
   - Be ready to optimize
   - Handle new constraints gracefully
   - Show adaptability

5. **Real-world Mindset**
   - Think about production scenarios
   - Consider monitoring and debugging
   - Discuss testing strategies

---

## 🔗 **RESOURCES**

### Practice Platforms:
- **LeetCode** - Premium for company-specific questions
- **HackerRank** - Good for product companies
- **Educative.io** - Pattern-based learning
- **NeetCode.io** - Video explanations

### System Design:
- **ByteByteGo** - Visual system design
- **Grokking System Design** (Educative)
- **System Design Interview by Alex Xu**

### Company Research:
- **Glassdoor** - Real interview experiences
- **Blind** - Anonymous company discussions
- **LeetCode Discuss** - Interview experiences
- **Company engineering blogs**

---

## 🎓 **FINAL ADVICE**

**The Golden Rules:**
1. **Consistency > Intensity** - 2 hours daily beats 14 hours on Sunday
2. **Understand, Don't Memorize** - Learn the "why" behind solutions
3. **Practice Out Loud** - Verbalize your thought process
4. **Review Your Mistakes** - Keep an error log
5. **Simulate Real Conditions** - Time yourself, no hints
6. **Focus on Patterns** - Recognize problem types quickly
7. **Build Projects** - For product companies, show real code
8. **Network** - Referrals significantly boost chances

**Remember:** Product companies (VMware, Atlassian, ServiceNow) value:
- Clean, maintainable code
- System thinking
- Production readiness
- Team collaboration
- Debugging skills

They often care MORE about how you think and communicate than just getting the optimal solution immediately.

---

Good luck with your preparation! 🚀

**Keep grinding, stay consistent, and trust the process!** 💪

---

*Last Updated: January 2026*
*Based on recent interview experiences from LeetCode, Glassdoor, and company-specific forums*

---

**Note:** Additional system design problems like payroll system design, vending machine design, and pet store design are covered in the system design practice recommendations above.