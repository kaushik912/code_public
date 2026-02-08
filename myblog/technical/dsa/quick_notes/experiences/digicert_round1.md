- This is just draft, i will add more examples later

arr= [2,1,3,4,2,5,1]

let s = new Set();


let map ={};
arr.forEach(val ={
    if(map[val]!=null){
        map[val]++;
    }else{
        map[val]=1;
    }
});

for (key in map){
    console.log(key);
}

[1,2,3,4,5]

---

counter

export default function counter(){
    [counter, setCounter] = useState(0);
    const setCounter = ()=>{
        let newCount = counter+1;
        setState(newCount);
    }
    return (
        <div>
               <button onClick={()=>setCounter}></button> 
               <text>{counter}</text>
        </div>
    );
}
---

// commit to db

// push to queue

// consumer
WithinClass Transaction
placeOrder(){
    // some tasks
    saveOrder();
}

@Transactional 
saveOrder() {

}

---
//want to run a single thread application
//SingleTHreadExecutor versus FixedThreadPool()
//
---
Drawbacks of Kafka
---