
 
# Getting Started 
Consider the following snippet
```
  button.addActionListener(
  new ActionListener(){
      public void actionPerformed(ActionEvent e){
          System.out.println("Button Clicked");
      }
  }
  )
```
As we can see, there are few observations
- Lots of *boilerplate* code
- It obscures the Programmer's intent
- We are giving button an object that represents an action ( we are using code as data)

Now, consider the following declaration
```
    button.addActionListener(
        event -> System.out.println("Button Clicked"));
```
It does the same job as before but we can see the following: 
- Block of code - a function without a name
- event is the name of the parameter
- Instead of an object that implements an interface, we are passing in a *block of code*.
- We don't provide the 'type' for event, *javac* infers it as an Action Event.
- 
Congrats! you've written your first *lambda* expression!


## Different ways of writing lambda expressions
Lets explore what are the different ways of writing lambda expressions

- No arguments, Eg: Java Runnable
```
  () -> System.out.println("Hello World!");
```
- One argument, Eg: ActionListener
```
  event -> System.out.println("Button Clicked");
```
- Multi-statements, Eg: again Runnable!
```
     () -> {
            System.out.println("Hello");
            System.out.println("World!");
     }
```
- BinaryOperator: Specialization of BiFunction where two operands of same type produce result of the same type as operands. In other words, BiFunction<T,T,T>
```
BinaryOperator<Long> add  = (x,y)-> x+y;
System.out.println(add.apply(1L,2L)); //Prints 3
```
- Two useful functions from the BiFunction
```
R apply( T t, T u)
default <V> BiFunction<T,U,V> andThen(Function<? super R,? extends V> after)
```

## What is Functional Interface?
A functional interface is an interface with a single abstract method that is used as a type of a lambda expression.

## Functional Interfaces in Java8.

| Function          	| Arguments 	| Returns 	| Method     	| Example                                    	|
|-------------------	|-----------	|---------	|------------	|--------------------------------------------	|
| Predicate<T>      	| T         	| boolean 	| test()     	| Is Album Released?                         	|
| Consumer<T>       	| T         	| void    	| accept()   	| Print out all track titles from this album 	|
| Supplier<T>       	| None      	| T       	| get()      	| A factory method                           	|
| UnaryOperator<T>  	| T         	| T       	| identity() 	| Logical not(!)                             	|
| BinaryOperator<T> 	| T,T       	| T       	| apply()    	| Multiply two nums                          	|
| Function<T,R>     	| T         	| R       	| apply()    	| Get name from Artist object                	|

These functional interfaces need to be imported using 
```
  import java.util.function.*;
```
# Exercises
## Exercise: We just now observed that ActionListener expects ActionEvent as an input and the method returns void. What is this type of Functional Interface?
Solution: Since it takes in input as T and returns void , looking into the table above, we observe its a consumer function!

## Exercise: Define a predicate such that it checks if a number is greater than 5.
Lets re-visit Predicate. Its an interface defined as shown below:
```
  public interface Predicate<T>{
      boolean test(T t);
  }
```
So it expects an input of type T and the *test()* method implementation should return a boolean.
Lets now define our predicate as: 
```
  Predicate<Integer> greaterThan5 = x -> x > 5;
```
Since we have defined our predicate using lambda expression, we could invoke the test() method like below: 
```
  import java.util.function.*;
  import java.util.stream.*;
  import static java.util.stream.Collectors.*;
  class Main {
      public static void main(String[] args) {
          Predicate<Integer> greaterThan5 = x -> x > 5;
          System.out.println(greaterThan5.test(10));//True
          System.out.println(greaterThan5.test(2));//False
      }
  }
```

## Exercise:Write a BinaryOperator lambda expression to multiply two longs

BinaryOperator extends BiFunction. It takes two arguments of the same type and returns result as same type as that of the arguments. 

So, in this case, we could do:
```
  BinaryOperator<Long> multiplyLongs = (x,y)->x*y;
```
Since it extends a BiFunction, we can call the *apply()* method.
```
  System.out.println(multiplyLongs.apply(10L,20L));//Prints 200
```
However, the below snippet
```
  BinaryOperator multiplyLongs = (x,y) -> x*y; // This wont' compile!
```
Its because Type isn't specified and it can't add Object, Object!
So we need to specify type like BinaryOperator<Long> , BinaryOperator<Integer> etc.

## Function Interface - Revisited
Now, lets talk about an important interface i.e. Function.

It is used a lot in Streaming API in Collections ( we'll discuss Streaming APIs in another post)

Its interface looks like:
```
  public interface Function<T,R>{
      R apply(T t);
  }
```
    So Function expects an input of type T and method returns an object of type R.

## Exercise: Write a Function lambda expression that calculates square-root of a number.
Hint: Take input as integer and return a double.

So we could create a lambda expression and then call *apply()* as shown below:
```
  Function<Integer,Double> sqrtFunction = (x) -> Math.sqrt(x);
  System.out.println(sqrtFunction.apply(100)); //Prints 10
```

## Exercise: Which of the following are valid Function<Long,Long> implementations?
```
  x -> x +1
  (x,y) -> x+1
  x -> x==1; 
```
Solution:

- x -> x +1 --> Valid, it takes x and returns x+1
- (x,y) -> x+1 --> invalid,This is actually a bi-function as it takes two arguments x and y instead of one
- x -> x==1; --> invalid , its returning a boolean instead of a long, so its actually a predicate

## Exercise:Implement a thread-safe DateFormat class. Hint: Explore ThreadLocal class.

Solution
In ThreadLocal, we have a method withInitial() that takes a supplier function.

Below is the sample code that creates a thread-safe DateFormat class :
```
ThreadLocal<DateFormatter> dfm = 
ThreadLocal.withInitial(
    ()-> new DateFormatter()
);
```
We can extend this ThreadLocal logic to create other thread-safe instances.


# Type Inference
In the below code, we can see the diamond <> operator.
It automatically infers the type based on the left side in Java8!
```
Map<String,String> map = new HashMap<>();
```
As discussed before, Type in Lambda expression is auto-inferred by javac.

## Exercise: Explicitly add Type to the argument in a Lambda Expression

We could do:
```
    button.addActionListener(
(ActionEvent) event -> System.out.println("Button Clicked"));
```
 As you can see, in certain cases, it increases **readability and reduces ambiguity** by explicitly specifying the type.

