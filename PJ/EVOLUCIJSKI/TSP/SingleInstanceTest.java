import Utility.RandomUtils;
import algorithms.GA;
import problems.TSP;

public class SingleInstanceTest {
    public static void main(String[] args) {
        String instance = "bays29.tsp";
        int dimension = 29;
        int maxFes = 1000 * dimension; // 29000 evaluations
        
        System.out.println("Testing " + instance + " with " + maxFes + " evaluations");
        
        // Test just 3 runs for now to see if it works
        for (int run = 0; run < 3; run++) {
            System.out.println("Run " + (run + 1) + "/3");
            
            TSP tsp = new TSP(instance, maxFes);
            GA ga = new GA(100, 0.8, 0.1);
            
            long startTime = System.currentTimeMillis();
            TSP.Tour bestTour = ga.execute(tsp);
            long endTime = System.currentTimeMillis();
            
            if (bestTour != null) {
                System.out.println("Result: " + bestTour.getDistance());
                System.out.println("Time: " + (endTime - startTime) + "ms");
                System.out.println("Evaluations used: " + tsp.getNumberOfEvaluations());
            } else {
                System.out.println("Error: No solution found");
            }
            System.out.println();
        }
        
        System.out.println("Test completed");
    }
}