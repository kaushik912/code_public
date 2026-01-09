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
    public static String firstMatch(String[] words, String note) {
       
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
- Build first the freq map of the note characters: {a:1,b:1,e:1,p:2,t:1,x:2,y:1,z:1}
- now, pick each word and build its freq map: 
    - eg: "peep", wordMap: {p:2, e:2}
    - We want all characters of word (with freq) to be present in note.
    - So, p:2 is present in both
    - e:2 in word but noteMap contains e:1
        - so its a miss!
        - wordMap.ch.count > noteMap.ch.count, then its a miss
        - So some character-counts in word are not available in note.
    - eg: "bat", {a:1,b:1,t:1}
        - all freq counts in "bat" are present in note
    - eg: "peat", wordMap = {p:1,e:1,a:1,t:1}
        - all characters of word are present in the note.
        - so "peat" is also a valid answer.
    - eg: "tan", wordMap = {t:1,a:1,n:1}
        - again n is not present in the noteMap. So its a miss.
        - noteMap.n==null here.
    - for a char ch in word,
        - if(noteMap.ch==null || (wordMap.ch.count > noteMap.ch.count ))
            - its a miss
        - otherwise that word is a pass. Why?
            - noteMap.ch is not null and it'll have count >=wordMap.ch.count.
            - So we would be able to obtain that word from the note.
### Key concept
    - Use maps to track counts
    - For every character c in the word, noteCount[c] >= wordCount[c], only then note fully "contains" the word.

