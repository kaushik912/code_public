# Page Fault
```
Given a sequence of pages in an array pages[] of length N and memory capacity C, find the number of page faults using Least Recently Used (LRU) Algorithm. 

Input: N = 9, C = 4
pages = {5, 0, 1, 3, 2, 4, 1, 0, 5}
Output: 8
```
```
Hint1:
Have a basic working idea of LRU to solve this problem.
```
```
Hint2: For quick solution if allowed, Use a LinkedHashSet<> to store Key
In LinkedHashSet<>, oldest will be at the front and newest will be towards the end.

if value exists in Set
    Remove the key in set
    Add this element to set ( newest will be at the end)
if value doesn't exist in set
    we need to either add or replace existing based on set.size and Capacity.
    if set.size()==C
        Remove oldest element (oldest will be in the beginning)
        In Java, beginning element can be accessed using set.iterator().next()
        Add this new element (new at the end)
    otherwise
        Add this new element to set ( new at the end)

Since we use a Set, all operations are O(1)

```
```
Hint2: Implement the above idea!
public int pageFaults(int[] nums, int C){

    LinkedHashSet<Integer> s = new LinkedHashSet<>();
    int pagefault=0;
    for(int num: nums){
        if(s.containsKey(num)){
            s.remove(num);    
        }else{
            pagefault++;
            // if it exceeded capacatiy
            if(s.size()==C){
                Integer first = s.iterator().next();
                s.remove(first);    
            }
        }
        s.add(num);
    }
    return pagefault;

}
```