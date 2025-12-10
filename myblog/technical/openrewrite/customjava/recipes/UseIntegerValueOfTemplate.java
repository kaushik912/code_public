package com.yourorg;

import com.google.errorprone.refaster.annotation.AfterTemplate;
import com.google.errorprone.refaster.annotation.BeforeTemplate;
import org.openrewrite.java.template.RecipeDescriptor;

@RecipeDescriptor(
        name = "UseIntegerValueOf",
        description = "Use Integer.valueOf(x) or Integer.parseInt(x) instead of new Integer(x)"
)
@SuppressWarnings("unused")
public class UseIntegerValueOfTemplate {

    // Recipe for int case: new Integer(int) -> Integer.valueOf(int)
    @RecipeDescriptor(
            name = "Replace new Integer(int) with Integer.valueOf(int)",
            description = "Replaces new Integer with an int argument with Integer.valueOf()"
    )
    public static class IntCase {
        @BeforeTemplate
        Integer before(int x) {
            return new Integer(x);
        }

        @AfterTemplate
        Integer after(int x) {
            return Integer.valueOf(x);
        }
    }

    // Recipe for String case: new Integer(String) -> Integer.parseInt(String)
    @RecipeDescriptor(
            name = "Replace new Integer(String) with Integer.parseInt(String)",
            description = "Replaces new Integer with a String argument with Integer.parseInt()"
    )
    public static class StringCase {
        @BeforeTemplate
        Integer before(String x) {
            return new Integer(x);
        }

        @AfterTemplate
        Integer after(String x) {
            return Integer.parseInt(x);
        }
    }
}