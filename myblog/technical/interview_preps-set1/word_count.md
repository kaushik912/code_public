
### Word Count Problem 

Lets say we have a list of words, and we want to store how many times each word appears in a `Map<String, Integer>`.

#### **Without `computeIfAbsent` (Manual Checking)**
```java
import java.util.*;

public class WordCountExample {
    public static void main(String[] args) {
        Map<String, Integer> wordCount = new HashMap<>();
        String[] words = {"apple", "banana", "apple", "orange", "banana", "apple"};

        for (String word : words) {
            if (!wordCount.containsKey(word)) {
                wordCount.put(word, 0);
            }
            wordCount.put(word, wordCount.get(word) + 1);
        }

        System.out.println(wordCount); // Output: {orange=1, banana=2, apple=3}
    }
}
```
---
#### **With `computeIfAbsent` (Simplified)**
```java
import java.util.*;

public class WordCountExample {
    public static void main(String[] args) {
        Map<String, Integer> wordCount = new HashMap<>();
        String[] words = {"apple", "banana", "apple", "orange", "banana", "apple"};

        for (String word : words) {
            wordCount.computeIfAbsent(word, k -> 0);
            wordCount.put(word, wordCount.get(word) + 1);
        }

        System.out.println(wordCount); // Output: {orange=1, banana=2, apple=3}
    }
}
```
---
#### **Even More Concise: Using `merge` Instead**
Alternatively, we can do:
```java
wordCount.merge(word, 1, Integer::sum);
```
which handles initialization and incrementing in one step.

---
### **How `computeIfAbsent` Works Here**
- If a word **does not exist** in the map, `computeIfAbsent` initializes it to `0`.
- Then, we simply increment the count.
