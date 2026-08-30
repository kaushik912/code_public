import java.util.ArrayList;
import java.util.List;

public class ThreeFourFix {
    public int[] fix34(int[] nums) {
        // identify 3 indexes
        // identify 4 indexes
        // swap 3's index+1 with 4's index
        List<Integer> threeIndices = new ArrayList<>();
        List<Integer> fourIndices = new ArrayList<>();
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] == 3) {
                threeIndices.add(i);
            }
            if (nums[i] == 4) {
                fourIndices.add(i);
            }
        }

        int k = 0;
        for (int threeIndex : threeIndices) {
            if (threeIndex + 1 < nums.length) {
                int fourIndex = fourIndices.get(k++);
                int temp = nums[threeIndex + 1];
                nums[threeIndex + 1] = nums[fourIndex];
                nums[fourIndex] = temp;
            }
        }

        return nums;

    }

    public static void main(String[] args) {
        ThreeFourFix threeFourFix = new ThreeFourFix();
        int[] result = threeFourFix.fix34(new int[] { 1, 3, 1, 4 });
        for (int num : result) {
            System.out.print(num + " ");
        }
    }

}
