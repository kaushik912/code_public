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
import java.util.*;

/**
 * Practice problem:
 * Given String[][] input where each row is: {songTitle, durationString}
 * durationString is a decimal with up to 2 places (e.g., "2.25", "3", "0.10").
 *
 * Implement findPair(String[][] input) to return a String[2] containing TWO song titles
 * whose durations sum to TARGET (defined below).
 *
 * Requirements for your implementation:
 * - Return exactly 2 titles if a valid pair exists, otherwise return an empty array new String[0].
 * - Do NOT use the same row/song twice.
 * - Durations are decimals; you must handle floating-point safely. (Hint: scaling to cents is common.)
 * - Assume input may contain duplicates (same duration / same title).
 */
public class SongPairPractice {

    // Each testcase sets this before calling findPair(input).
    static double TARGET = 0.0;

    // Tolerance only used by the test harness validator (not a solution hint for your approach).
    static final double EPS = 1e-9;

    /**
     * TODO: Implement this.
     * @param input array of {title, durationString}
     * @return String[2] with the pair of song titles that sum to TARGET, else empty array
     */
    public static String[] findPair(String[][] input) {
        // DO NOT IMPLEMENT HERE (for your practice)
        throw new UnsupportedOperationException("TODO: implement findPair");
    }

    // ---------------------- Test Harness (main) ----------------------

    public static void main(String[] args) {
        int passed = 0;
        int total = 0;

        // Test 1: simple exact decimals (should find a pair)
        total++;
        TARGET = 4.00;
        String[][] t1 = {
                {"A", "2.25"},
                {"B", "1.75"},
                {"C", "0.50"},
                {"D", "3.50"}
        };
        if (runTest("Test 1 (exact .25/.75)", t1, true)) passed++;

        // Test 2: classic floating-point trap values (0.10 + 0.20 = 0.30)
        // With naive double hashing/equality, many solutions fail. With proper normalization, it passes.
        total++;
        TARGET = 0.30;
        String[][] t2 = {
                {"S1", "0.10"},
                {"S2", "0.20"},
                {"S3", "0.40"},
                {"S4", "0.30"}
        };
        if (runTest("Test 2 (0.10 + 0.20)", t2, true)) passed++;

        // Test 3: multiple possible pairs (any valid pair is acceptable)
        total++;
        TARGET = 3.00;
        String[][] t3 = {
                {"P", "1.00"},
                {"Q", "2.00"},
                {"R", "1.50"},
                {"S", "1.50"},
                {"T", "3.00"} // note: single song equals target, but you must return a pair of TWO songs
        };
        if (runTest("Test 3 (multiple valid pairs)", t3, true)) passed++;

        // Test 4: duplicates + ensure you don't reuse the same song row twice
        total++;
        TARGET = 2.00;
        String[][] t4 = {
                {"X1", "1.00"},
                {"X2", "1.00"},
                {"Y",  "0.50"},
                {"Z",  "1.50"}
        };
        if (runTest("Test 4 (duplicate durations, distinct rows)", t4, true)) passed++;

        // Test 5: no solution
        total++;
        TARGET = 10.00;
        String[][] t5 = {
                {"AA", "1.25"},
                {"BB", "2.50"},
                {"CC", "3.75"}
        };
        if (runTest("Test 5 (no pair)", t5, false)) passed++;

        // Test 6: durations with 2 decimals, includes leading/trailing zeros
        total++;
        TARGET = 6.20;
        String[][] t6 = {
                {"LZ", "01.20"},
                {"TZ", "5.00"},
                {"M1", "3.10"},
                {"M2", "3.10"}
        };
        if (runTest("Test 6 (format variations)", t6, true)) passed++;

        // Summary
        System.out.println("\n==============================");
        System.out.println("Passed " + passed + " / " + total + " tests.");
        System.out.println("==============================");
    }

    /**
     * Runs a testcase and validates the returned pair.
     *
     * This validator checks correctness without forcing you into a specific algorithm.
     * It will accept ANY pair of two titles that sums to TARGET (within a tiny tolerance).
     */
    private static boolean runTest(String name, String[][] input, boolean expectPair) {
        System.out.println("\n--- " + name + " | TARGET=" + TARGET + " ---");
        try {
            String[] ans = findPair(input);

            if (!expectPair) {
                if (ans == null || ans.length == 0) {
                    System.out.println("OK: returned empty as expected.");
                    return true;
                } else {
                    System.out.println("FAIL: expected empty, got: " + Arrays.toString(ans));
                    return false;
                }
            }

            // expectPair == true
            if (ans == null || ans.length != 2) {
                System.out.println("FAIL: expected String[2], got: " + Arrays.toString(ans));
                return false;
            }

            if (!validatePair(input, ans[0], ans[1], TARGET)) {
                System.out.println("FAIL: invalid pair " + Arrays.toString(ans));
                return false;
            }

            System.out.println("OK: valid pair found: " + Arrays.toString(ans));
            return true;

        } catch (UnsupportedOperationException e) {
            System.out.println("TODO: Implement findPair to run tests.");
            return false;
        } catch (Exception e) {
            System.out.println("FAIL with exception: " + e);
            e.printStackTrace(System.out);
            return false;
        }
    }

    /**
     * Validates:
     * - titles exist in input (as rows)
     * - uses two DISTINCT rows (cannot reuse the same row)
     * - sum of durations equals target within tolerance
     */
    private static boolean validatePair(String[][] input, String title1, String title2, double target) {
        // Find all matching rows for title1/title2 (titles may repeat)
        List<Integer> idx1 = new ArrayList<>();
        List<Integer> idx2 = new ArrayList<>();

        for (int i = 0; i < input.length; i++) {
            if (input[i] == null || input[i].length < 2) continue;
            if (Objects.equals(input[i][0], title1)) idx1.add(i);
            if (Objects.equals(input[i][0], title2)) idx2.add(i);
        }

        if (idx1.isEmpty() || idx2.isEmpty()) return false;

        // Try all combinations of distinct rows
        for (int i : idx1) {
            for (int j : idx2) {
                if (i == j) continue;

                Double d1 = parseDuration(input[i][1]);
                Double d2 = parseDuration(input[j][1]);
                if (d1 == null || d2 == null) continue;

                if (Math.abs((d1 + d2) - target) < EPS) return true;
            }
        }
        return false;
    }

    private static Double parseDuration(String s) {
        if (s == null) return null;
        try {
            return Double.parseDouble(s.trim());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
```

