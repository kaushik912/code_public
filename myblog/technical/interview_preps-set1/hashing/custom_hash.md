Here’s a **concise interview prep guide** based on our discussion about **data structures, hashing, and hash tables in Java**. It’s designed so someone can skim it before an interview and quickly recall the essentials.

---

# 🚀 Hash Tables & String Hashing – Interview Quick Guide

## 1. Data Structures vs Algorithms
- **Data Structure** = container (e.g., array, hash table, tree).  
- **Algorithm** = behavior (e.g., sorting, searching, hashing).  
👉 Example: Array holds numbers, QuickSort arranges them.

---

## 2. Hash Tables – Core Idea
- Store key–value pairs.  
- Lookup is **average O(1)** using a hash function.  
- Bucket index = `hash(key) % table_size`.

---

## 3. Collisions
- **Collision** = two keys map to the same bucket.  
- Handling strategies:
  - **Chaining** → each bucket holds a linked list of entries.  
  - **Open addressing** → probe for next available slot.  

👉 Chaining is simpler to implement.

---

## 4. Hash Functions
A good hash function should:
- Spread keys **uniformly** across buckets.  
- Be **fast** to compute.  
- Use **all characters** (not just length or first character).  

### Polynomial Rolling Hash (common for strings):
\[
\text{hash}(s) = (s_0 \cdot p^0 + s_1 \cdot p^1 + s_2 \cdot p^2 + \dots) \mod m
\]

- \(p\) = prime base (e.g., 31).  
- \(m\) = large prime modulus (e.g., \(10^9+7\)).  
- Ensures both **content** and **order** matter.

---

## 5. Resizing (Rehashing)
- When load factor > ~0.75, resize table (usually double capacity).  
- All keys must be **rehashed** because modulus changes.  
- Roughly half of keys stay in same bucket, half move (if distribution is uniform).

---

## 6. Java Implementation – Custom Hash Table

```java
import java.util.LinkedList;

class CustomHashTable {
    private LinkedList<Entry>[] table;
    private int capacity;
    private int size;
    private final int P = 31;
    private final int M = 1_000_000_009;

    static class Entry {
        String key, value;
        Entry(String k, String v) { key = k; value = v; }
    }

    @SuppressWarnings("unchecked")
    public CustomHashTable(int capacity) {
        this.capacity = capacity;
        table = new LinkedList[capacity];
        for (int i = 0; i < capacity; i++) table[i] = new LinkedList<>();
    }

    private int hash(String key) {
        long hashValue = 0, power = 1;
        for (char c : key.toCharArray()) {
            hashValue = (hashValue + (c - 'a' + 1) * power) % M;
            power = (power * P) % M;
        }
        return (int)(hashValue % capacity);
    }

    public void put(String key, String value) {
        int index = hash(key);
        for (Entry e : table[index]) {
            if (e.key.equals(key)) { e.value = value; return; }
        }
        table[index].add(new Entry(key, value));
        size++;
    }

    public String get(String key) {
        int index = hash(key);
        for (Entry e : table[index]) if (e.key.equals(key)) return e.value;
        return null;
    }

    public void remove(String key) {
        int index = hash(key);
        table[index].removeIf(e -> e.key.equals(key));
    }
}
```

### Demo:
```java
public static void main(String[] args) {
    CustomHashTable ht = new CustomHashTable(10);
    ht.put("cat", "feline");
    ht.put("dog", "canine");
    ht.put("bat", "mammal");

    System.out.println(ht.get("cat")); // feline
    System.out.println(ht.get("dog")); // canine
    ht.remove("dog");
    System.out.println(ht.get("dog")); // null
}
```

---

## 7. Interview Takeaways
- **Know the difference**: data structure vs algorithm.  
- **Explain collisions** and handling strategies.  
- **Discuss hash function design** (uniform distribution, polynomial rolling hash).  
- **Understand resizing** and why rehashing is needed.  
- **Be ready to code** a simple hash table with chaining.  

---
