package com.example.helloworld;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class StaticAnalysisRefactorExample {

    // ❌ Mutable argument, should be final or copied.
    public static void addDefaultName(List<String> names) {
        if (names == null) { // ❌ Should use defensive checks and return early.
            names = new ArrayList<>();
        }
        names.add("John Doe");
    }

    // ❌ Magic number "42" should be replaced with a constant.
    public static int computeAnswer(int input) {
        int result = input * 42;
        if (result == 0) { // ❌ Redundant conditional check could be simplified
            return 0;
        }
        return result;
    }

    // ❌ Resource leak: FileReader not closed properly.
    public static void readFile(String path) {
        try {
            BufferedReader reader = new BufferedReader(new FileReader(path));
            String line = reader.readLine();
            while (line != null) {
                System.out.println(line);
                line = reader.readLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // ❌ Unused local variable and redundant string concatenation.
    public static void greet(String name) {
        String greeting = "Hello " + name + "!"; // variable never used
        System.out.println("Hi " + name + "!");
    }

    // ❌ Missing @Override annotation.
    static class Animal {
        public void speak() {
            System.out.println("Generic sound");
        }
    }

    static class Dog extends Animal {
        public void speak() { // should have @Override
            System.out.println("Bark");
        }
    }

    // ❌ Inefficient list initialization and unused import.
    public static List<String> buildList(String[] items) {
        List<String> list = new ArrayList<>();
        for (int i = 0; i < items.length; i++) { // ❌ Could use enhanced for loop
            list.add(items[i]);
        }
        return list;
    }

    private StaticAnalysisRefactorExample() {
    }
}
