### How to compute frequency count in Java
```
Assume we have a map like below:
Map<String,Integer>
If I provide an array of strings: "happy","sad","happy","sorrow"
it should return the frequency count of the strings.
```
```
Hint1: Use Java7, verbose, old-school, always safe!
for(String word: words){
  if(map.containsKey(word)){
    map.put(word,map.get(word)+1);
  }else{
    map.put(word,1);
  }
}

Hint2: Use Java8 Preferred for freq-counts
map.put(word,map.getOrDefault(word, 0)+1);

Hint3: use ComputeIfAbsent for objects, esp. multi-valued maps.
map.computeIfAbsent("Bangalore", k -> new ArrayList<>()).add("Ram");
// All compute() methods return the new value.

Hint4: Least Preferred
Using map.compute (less preferred, do not use this, people often get confused)
map.compute( word, (k,v)-> v==null? 1 : v+1);
```