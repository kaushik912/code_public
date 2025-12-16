package com.example.helloworld;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class StaticAnalysisRefactorTarget {

    // ❌ Missing @Override
    static class Animal {
        public void speak() {
            System.out.println("Generic sound");
        }
    }

    static class Dog extends Animal {
        public void speak() { // Missing @Override
            System.out.println("Bark!");
        }
    }

    // ❌ Mutable argument; should be final
    // ❌ Redundant if logic; ❌ Magic number; ❌ Unused variable
    public static int processData(List<String> items, int multiplier) {
        int result = 0;
        if (items.size() > 0) { // Redundant check
            for (int i = 0; i < items.size(); i++) { // could use enhanced for
                result += i * multiplier * 42; // Magic number
            }
        } else {
            result = 0;
        }
        String unused = "This variable is never used";
        return result;
    }

    // ❌ Resource leak: FileReader never closed properly
    public static void readFile(String path) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(path));
        String line;
        while ((line = reader.readLine()) != null) {
            System.out.println(line);
        }
    }

    // ❌ Simplifiable boolean return
    public static boolean isPositive(int n) {
        if (n > 0) {
            return true;
        } else {
            return false;
        }
    }

    // ❌ Inefficient generics instantiation (no diamond operator)
    // ❌ Unused import in the file
    public static List<String> makeList(String a, String b) {
        List<String> list = new ArrayList<String>();
        list.add(a);
        list.add(b);
        return list;
    }
}
