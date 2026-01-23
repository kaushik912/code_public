## Problem: First Dictionary Word Scrambled in a Note

You are given:

* a list of dictionary words `words`
* a string `note`

A word is considered **present in scrambled form** inside the note if **all characters of the word can be picked from the note** (in any order), and **each character can be used at most as many times as it appears in the note**.

Return the **first word (by list order)** that can be formed from the note.
If no word can be formed, return an empty string.

Assume input contains lowercase English letters `a-z`.

---

## Examples

### Example 1 (fixed)

**Input**

* `words = ["peep", "bat", "peat", "tan", "pet"]`
* `note = "xxaetppbyz"`

**Output**

* `"bat"`

**Why**

* `"peep"` needs 2 `'e'`, note has only 1 → ❌
* `"bat"` needs `b,a,t`, all exist in the note → ✅ first match

### Example 2

**Input**

* `words = ["aaa", "bbb", "abc"]`
* `note = "ab"`

**Output**

* `""`

### Example 3 (duplicates matter)

**Input**

* `words = ["aab", "aba", "baa"]`
* `note = "aba"`

**Output**

* `"aab"` (first by list order)

---

## Java Reference Solution (Map<Character, Integer>) + Testcases

```java
import java.util.*;

public class FirstScrambledWord {

    // Return the first word that can be formed from note; else ""
    public static String firstMatch(List<String> words, String note) {
       
        return "";
    }

    // ---- Tests ----
    public static void main(String[] args) {
        runTests();
        System.out.println("All tests passed ✅");
    }

    private static void runTests() {
        test(
            Arrays.asList("peep", "bat", "peat", "tan", "pet"),
            "xxaetppbyz",
            "bat"
        );

        test(
            Arrays.asList("aaa", "bbb", "abc"),
            "ab",
            ""
        );

        test(
            Arrays.asList("aab", "aba", "baa"),
            "aba",
            "aab"
        );

        test(
            Arrays.asList("hello", "world"),
            "dlrowxx",
            "world"
        );

        test(
            Arrays.asList("abc", "aabbcc", "cab"),
            "abcc",
            "abc"
        );

        test(
            Arrays.asList("zzz", "zz", "z"),
            "zz",
            "zz"
        );
    }

    private static void test(List<String> words, String note, String expected) {
        String actual = firstMatch(words, note);
        if (!Objects.equals(actual, expected)) {
            throw new AssertionError(
                "FAILED\nwords=" + words +
                "\nnote=" + note +
                "\nexpected=" + expected +
                "\nactual=" + actual
            );
        }
    }
}
```

## My notes
- We want to check if word exists in note
- order of characters do not matter.

* `words = ["peep", "bat", "peat", "tan", "pet"]`
* `note = "xxaetppbyz"`
* output is "bat"

### Approach
```
    // Its a note to word puzzle
    // to form a particular word, all char-freqs in word must be present in note.
    // if any char-freq of word is missing in note, that word cannot be formed.
     // if this rule doesn't break, then word can be formed from the note.

    // Approach1: 
    // we create a char-freq map of the note
    // for each word
        // start with a fresh copy of the note map (since we decrement on seeing char matches for each fresh word)
        // check if its char is present in note map
            // if not, reject, move to next word
            // if present,
                // decrement the freq-count in the map
                // if count reaches 0, remove that key from map
            // if you have reach the end of word without getting rejected, you found the match!
   
    // Approach2 ( Two freq maps, this is also neat)
    // eg: note: "bata", words=["bat","battalion","cat"]
    // we create a char-freq map of the note
        // for each word
        // Build a word-freq map
        // for each character ch in word
            // note-freq.ch.count should be >= word-freq.ch.count
            // otherwise you can't make the word from the note!
            // special case: note-freq.ch could be null ( that character itself isn't present in note but present in word)
    
```

## Key Concepts
    - Use char-freq maps for words and note
    - Use "reduction" logic to rule out cases when word can't be made from note.
