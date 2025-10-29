package com.yourorg.testsamples;

public class Test {
    boolean trueCondition1 = true ? true : false;
    boolean trueCondition2 = false ? false : true;
    boolean trueCondition3 = booleanExpression() ? true : false;
    boolean trueCondition4 = trueCondition1 && trueCondition2 ? true : false;
    boolean trueCondition5 = !true ? false : true;
    boolean trueCondition6 = !false ? true : false;

    boolean falseCondition1 = true ? false : true;
    boolean falseCondition2 = !false ? false : true;
    boolean falseCondition3 = booleanExpression() ? false : true;
    boolean falseCondition4 = trueCondition1 && trueCondition2 ? false : true;
    boolean falseCondition5 = !false ? false : true;
    boolean falseCondition6 = !true ? true : false;

    boolean binary1 = booleanExpression() && booleanExpression() ? true : false;
    boolean binary2 = booleanExpression() && booleanExpression() ? false : true;
    boolean binary3 = booleanExpression() || booleanExpression() ? true : false;
    boolean binary4 = booleanExpression() || booleanExpression() ? false : true;

    boolean booleanExpression() {
        return true;
    }
}