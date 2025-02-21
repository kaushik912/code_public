
### Rearrange array in such a way that all even numbers are to the left and odd numbers are to the right


```java
import java.util.Arrays;
import java.util.List;

public class NumberSeparator {
    public static int moves(List<Integer> arr) {
        int left = 0;
        int right = arr.size() - 1;
        int swapCount = 0;

        if (arr.size() < 2) {
            return 0; // No swaps needed
        }

        while (left < right) {
            // Move left pointer to the right until an odd number is found
            while (left < right && arr.get(left) % 2 == 0) {
                left++;
            }
            // Move right pointer to the left until an even number is found
            while (left < right && arr.get(right) % 2 != 0) {
                right--;
            }

            // Swap only if pointers are still in valid range
            if (left < right) {
                swap(arr, left, right);
                left++;
                right--;
                swapCount++;
            }
        }
        return swapCount;
    }

    private static void swap(List<Integer> arr, int left, int right) {
        int temp = arr.get(left);
        arr.set(left, arr.get(right));
        arr.set(right, temp);
    }

    private static void test(List<Integer> arr, int expectedSwaps) {
        System.out.println("Original List: " + arr);
        int swaps = moves(arr);
        System.out.println("Reordered List: " + arr);
        System.out.println("Swaps Performed: " + swaps + " (Expected: " + expectedSwaps + ")");
        System.out.println("----------------------------------");
    }

    public static void main(String[] args) {
        // Test cases
        test(Arrays.asList(13, 10, 20, 21), 1); // Expected: [20, 10, 13, 21], 1 swap
        test(Arrays.asList(2, 4, 6, 9, 11), 0); // Already sorted, 0 swaps
        test(Arrays.asList(1, 3, 5, 7), 0); // All odd, 0 swaps
        test(Arrays.asList(5, 2, 9, 4, 3, 6, 7, 8), 3); // Mixed case, 3 swaps
        test(Arrays.asList(10), 0); // Single element, 0 swaps
        test(Arrays.asList(), 0); // Empty list, 0 swaps
    }
}


```


