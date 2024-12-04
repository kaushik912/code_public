
In this post, we'll discuss some common Stream Operations

- collect(Collectors.toList())
    This is a *eager* operation. Below is one such example
    ```
    List<String> collected = Stream.of("a","b","c").collect(Collectors.toList());
    assertEquals(Arrays.asList("a","b","c"),collected);
    ```
    We convert the values from Stream to List.

- Convert Strings to uppercase

    - Java7 way
    ```
    List<String> collected = new ArrayList<>();
    for (String string : asList("a","b","hello")){
        String upperCase = string.toUpperCase();
        collected.add(upperCase);
    }
    ```

    - Java8 way
    ```
    List<String> collected = Stream
        .of("a","b","hello")
        .map( string -> string.toUpperCase())
        .collect(toList());
    ```
- Identify strings starting with a number

    - Java7 way
    ```
    List<String> beginningWithNumber = new ArrayList<>();
    for (String string : asList("a","b","hello")){
        if(isDigit(string.charAt(0)))
        beginningWithNumber.add(string);
    }
    ```
    - Java8 way
    ```
    List<String> beginningWithNumber = Stream
        .of("a","b","hello")
        .filter( string -> isDigit(string.charAt(0)))
        .collect(toList());
```
Note: Here, functional interface for the filter is a Predicate.



