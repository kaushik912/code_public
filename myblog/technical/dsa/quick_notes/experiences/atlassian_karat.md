# First question was about system design
- It was an ecommerce site.
- The web-app was the client
- There was a load-balancer 
- Beneath that, there were servers(microservice).
- Servers were talking to Product Database
 - There was mention of sharding at ProductId across the db instances
- There was also a Client DB
    - There was an admin-client that only had permission to access/update Client /Product metadata
- There was a replica job that used to run everyday 3pm. It used to copy client data into product DB.
- Then there were Kiosks that were directly talking to Product DB
    - They had a cache which had most recently purchased items
    - It was invalidated every minute.

### Question was to improve the above design
- I talked about CDN for serving static content ( based on my GCP knowledge of Storage object)
- Also, talked about having a cache to avoid directly calling DB from the server( microservice)
- Then, regarding DB choice, I talked about having noSQL for reads and OLTP/transactional DB for writes.
    - Data that is not changing often like product information and other metadata could sit in NoSQL
    - Data that is payment related or transactional should sit in OLTP
- also, I mentioned that scheduler/replica job should run at non-peak hours, not 3 PM.
- I also talked about having rate-limiter in load-balancer to protect against Denial of service attacks
- It was open-ended. So I gave suggestions on the above design.

### Tips to improve
- Adding a gateway before the microservice is a good idea. Benefits include: 
    - It acts like a reverse-proxy
    - It protects backend services from abuse
    - It enforces auth once (JWT) instead of every microservice implementing it.
    - Route requests to correct microservice (/v1/products), (/v2/new)
    - It can have rate-limiter

- Kiosks shouldn't directly be calling to DB. They should instead be calling a Kiosk API/Gateway -> Services -> DB.
- Blanket TTL invalidation (of 1 minute) is not a good idea. It could be done only when products change.
    - Use different TTLs depending on how often the item varies
- Apart from Sharding, It is good to add a search layer( ElasticSearch) for Browse/Search cases .
    - Also adding secondary indexes will boost the query performance ( around category, etc.)
- Instead of a cron job (which is run every 24 hours), use a Pub/Sub (Kafka) to update the client information into Product. It will have fresher data.


# Question 2
```java
public class SongPairPractice {

    static final double TARGET = 8.0;

    public static String[] findPair(String[][] input) {
       //Implement this
        return new String[0];
    }

    public static void main(String[] args) {

        // ---------- Positive Test 1 (single valid pair) ----------
        String[][] t1 = {
                {"A", "2.25"},
                {"B", "5.75"}, // ✅ only valid pair
                {"C", "1.10"},
                {"D", "6.20"},
                {"E", "3.30"},
                {"F", "4.40"}
        };
        System.out.println(Arrays.toString(findPair(t1)));
        // Expected: [A, B]


        // ---------- Positive Test 2 (leading zeros) ----------
        String[][] t2 = {
                {"M", "01.20"},
                {"N", "6.80"}, // ✅ only valid pair
                {"O", "0.50"},
                {"P", "2.10"},
                {"Q", "3.40"},
                {"R", "7.30"}
        };
        System.out.println(Arrays.toString(findPair(t2)));
        // Expected: [M, N]


        // ---------- Positive Test 3 (duplicate durations) ----------
        String[][] t3 = {
                {"X1", "4.00"},
                {"X2", "4.00"}, // ✅ only valid pair
                {"Y",  "1.25"},
                {"Z",  "6.60"},
                {"W",  "2.35"}
        };
        System.out.println(Arrays.toString(findPair(t3)));
        // Expected: [X1, X2]


        // ---------- Positive Test 4 (0.xx values) ----------
        String[][] t4 = {
                {"S", "0.10"},
                {"T", "7.90"}, // ✅ only valid pair
                {"U", "0.20"},
                {"V", "7.70"},
                {"W", "3.33"},
                {"X", "4.44"}
        };
        System.out.println(Arrays.toString(findPair(t4)));
        // Expected: [S, T]


        // ---------- Negative Test (no valid pair) ----------
        String[][] tNeg = {
                {"A", "1.25"},
                {"B", "2.40"},
                {"C", "3.35"},
                {"D", "4.10"},
                {"E", "5.60"},
                {"F", "6.75"}
        };
        System.out.println(Arrays.toString(findPair(tNeg)));
        // Expected: []
    }
}
```
- This problem is the classic two-sum problem (we could solve using Hash or two-pointer based approach)
- Two-pointer approach: we sort the array and move the pointer from either ends.
- Hash Approach: Since also need the titles back, we need a hash-map.
    - Store a Duration,Title map
    - When we get the complement Duration, we use the map to get the corresponding title and return
- Few caveats:
    - Floating point arithmetic may cause issues.
    - Best is to convert durations to BigDecimal and use those APIs rather than raw math.
    - Another option is to scale it to 100. (in case values are always 2 decimal points)
        - so, 0.10 becomes 10, 7.90 becomes 790 and target becomes 800 ( 10 + 790)
        

