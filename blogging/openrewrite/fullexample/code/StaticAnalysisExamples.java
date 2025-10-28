package com.example.helloworld;

public class StaticAnalysisExamples {

    // ❌ Utility class pattern violated: public constructor exists even though everything is static.
    //    HideUtilityClassConstructor should make this constructor private (and may make the class final).
    public StaticAnalysisExamples() { }

    // ❌ EqualsAvoidsNull: calling equals on a possibly-null reference.
    //    Should become "foo".equals(s)
    public static boolean isFoo(String s) {
        return s.equals("foo");
    }

    // Another EqualsAvoidsNull case, with different constant and in an if-statement.
    public static boolean isYes(String input) {
        if (input.equals("yes")) {
            return true;
        }
        return false;
    }

    // ❌ ReplaceStringBuilderWithString: trivial builder usage should be replaced with plain concatenation.
    public static String greet(String name) {
        StringBuilder sb = new StringBuilder("Hello, ");
        sb.append(name);
        sb.append("!");
        return sb.toString();
    }

    // Another trivial StringBuilder chain to trigger replacement.
    public static String path(String dir, String file) {
        return new StringBuilder(dir).append("/").append(file).toString();
    }

    // ❌ Utility method to keep class "utility-like" (all static members)
    public static int add(int a, int b) {
        return a + b;
    }

    // An inner utility class to trigger HideUtilityClassConstructor again.
    public static class Utils {
        // Implicit public no-arg constructor (❌) — should be made private
        public static String joinWithComma(String a, String b) {
            StringBuilder sb = new StringBuilder(a);
            sb.append(", ");
            sb.append(b);
            return sb.toString(); // ❌ ReplaceStringBuilderWithString
        }

        public static boolean isBar(String s) {
            return s.equals("bar"); // ❌ EqualsAvoidsNull
        }
    }
}
