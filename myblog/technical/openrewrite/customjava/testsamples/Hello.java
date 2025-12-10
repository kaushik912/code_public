package com.yourorg.testsamples;

public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello!");
        String str="hello!";
        if(str.length()==0){
            System.out.println("Empty String!");
        }

       // Before
        //Using a deprecated piece of code
        Integer num1 = new Integer(42);
        Integer num2 = new Integer("123");

        // After
        //Integer num1 = Integer.valueOf(42);
        //Integer num2 = Integer.parseInt("123");
    }
}
