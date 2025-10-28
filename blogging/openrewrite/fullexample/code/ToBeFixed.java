package com.example.helloworld;
import java.util.*;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;

public class ToBeFixed {

    public static void main(String[] args) {
        // --- singleton* recipes ---
        List<String> oneA = Collections.singletonList("a");          // MigrateCollectionsSingletonList
        Set<Integer> one42 = Collections.singleton(42);              // MigrateCollectionsSingletonSet
        Map<String, Integer> singleEntry = Collections.singletonMap("k", 1); // MigrateCollectionsSingletonMap

        // Use sites for those collections
        System.out.println(oneA.get(0));
        System.out.println(one42.contains(42));
        System.out.println(singleEntry.get("k"));

        // --- unmodifiable* recipes ---
        List<String> baseList = new ArrayList<>();
        baseList.add("x");
        baseList.add("y");
        List<String> unmodList = Collections.unmodifiableList(baseList); // MigrateCollectionsUnmodifiableList

        Set<String> baseSet = new HashSet<>();
        baseSet.add("p");
        baseSet.add("q");
        Set<String> unmodSet = Collections.unmodifiableSet(baseSet);     // MigrateCollectionsUnmodifiableSet

        // Observe they’re unmodifiable at runtime
        System.out.println(unmodList);
        System.out.println(unmodSet);

        // --- ReplaceStreamCollectWithToList ---
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4);

        // Qualified form
        List<String> asStrings1 = numbers.stream()
                .map(Object::toString)
                .collect(Collectors.toList()); // ReplaceStreamCollectWithToList

        // Static-import form
        List<Integer> evens1 = numbers.stream()
                .filter(n -> n % 2 == 0)
                .collect(toList()); // ReplaceStreamCollectWithToList

        // A couple more variations
        List<Integer> squares = numbers.stream()
                .map(n -> n * n)
                .collect(Collectors.toList()); // ReplaceStreamCollectWithToList

        List<String> copiedUnmodifiableThenCollected = Collections.unmodifiableList(
                new ArrayList<>(numbers.stream().map(Object::toString).collect(Collectors.toList())) // ReplaceStreamCollectWithToList
        );

        System.out.println(asStrings1);
        System.out.println(evens1);
        System.out.println(squares);
        System.out.println(copiedUnmodifiableThenCollected);
    }

    // Extra methods to cover non-local usage sites

    static List<String> makeSingletonList(String v) {
        return Collections.singletonList(v); // MigrateCollectionsSingletonList
    }

    static Set<String> makeSingletonSet(String v) {
        return Collections.singleton(v);     // MigrateCollectionsSingletonSet
    }

    static Map<String, String> makeSingletonMap(String k, String v) {
        return Collections.singletonMap(k, v); // MigrateCollectionsSingletonMap
    }

    static List<String> wrapUnmodifiable(List<String> in) {
        return Collections.unmodifiableList(in); // MigrateCollectionsUnmodifiableList
    }

    static Set<String> wrapUnmodifiable(Set<String> in) {
        return Collections.unmodifiableSet(in);  // MigrateCollectionsUnmodifiableSet
    }

    static List<String> collectToListExample(Collection<?> in) {
        return in.stream().map(Object::toString).collect(Collectors.toList()); // ReplaceStreamCollectWithToList
    }

    static List<Integer> staticImportCollectToListExample(List<Integer> in) {
        return in.stream().filter(Objects::nonNull).collect(toList()); // ReplaceStreamCollectWithToList
    }
}
