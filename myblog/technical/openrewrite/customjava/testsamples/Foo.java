package com.yourorg.testsamples;

public class Foo {
    boolean unsafe1(String actual) {
        return actual.equals("literal");
    }

    boolean unsafe2(String actual) {
        return actual.equals("foo");
    }

    boolean unsafe3(String str) {
        return str.equals("bar");
    }

    boolean nullsafe1(String actual) {
        return actual != null && actual.equals("literal");
    }

    boolean nullsafe2(String actual) {
        return actual != null && actual.equals("foo");
    }

    boolean complexCondition(String name) {
        return name.equals("admin") && true;
    }

    boolean multipleEquals(String a, String b) {
        return a.equals("test") || b.equals("demo");
    }

    boolean nested(String value) {
        if (value.equals("check")) {
            return true;
        }
        return false;
    }
}