import java.util.HashMap;
import java.util.Map;

public class Span {
    public int maxSpan(int[] nums) {
        // suppose i store first and last index for each value in array
        // {1:{0,3}
        // {2:{1,1}
        // {3:{4,4}
        // Calculate span as 3-0+1 = 4 for 1
        // 2 as 1, 3 as 1
        // so maxSpan is 4

        Map<Integer, int[]> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            final int j = i;
            map.compute(nums[i], (k, v) -> {
                if (v == null) {
                    v = new int[2];
                    v[0] = j;
                    v[1] = j;
                } else {
                    v[1] = j;
                }
                return v;
            });

        }
        
        int[] maxSpan = new int[1];
        map.forEach((k, v) -> {
            int span = v[1] - v[0] + 1;
            maxSpan[0] = Math.max(span, maxSpan[0]);
        });

        return maxSpan[0];

    }

    public static void main(String[] args) {
        Span span = new Span();
        System.out.println(span.maxSpan(new int[] { 1, 2, 1, 1, 3 }));
    }
}
