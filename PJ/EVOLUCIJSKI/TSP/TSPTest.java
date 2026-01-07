import Utility.RandomUtils;
import algorithms.GA;
import problems.TSP;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class TSPTest {

    public static void main(String[] args) {
        String[] instances = {"bays29.tsp", "eil101.tsp", "a280.tsp", "pr1002.tsp", "dca1389.tsp"};
        int[] dimensions = {29, 101, 280, 1002, 1389};
        
        // Use default seed for testing as specified in instructions
        
        for (int instanceIndex = 0; instanceIndex < instances.length; instanceIndex++) {
            String instance = instances[instanceIndex];
            int dimension = dimensions[instanceIndex];
            int maxFes = 1000 * dimension;
            
            System.out.println("Running " + instance + " with maxFes: " + maxFes);
            
            List<Double> results = new ArrayList<>();
            
            for (int run = 0; run < 30; run++) {
                TSP tsp = new TSP(instance, maxFes);
                GA ga = new GA(100, 0.8, 0.1);
                TSP.Tour bestTour = ga.execute(tsp);
                
                if (bestTour != null) {
                    results.add(bestTour.getDistance());
                    System.out.println("Run " + (run + 1) + ": " + bestTour.getDistance());
                }
            }
            
            saveResults(instance, results);
        }
        
        RandomUtils.setSeedFromTime();
        System.out.println("Final seed: " + RandomUtils.getSeed());
    }
    
    private static void saveResults(String instance, List<Double> results) {
        String filename = "results_" + instance.replace(".tsp", ".txt");
        try (FileWriter writer = new FileWriter(filename)) {
            for (double result : results) {
                writer.write(result + "\n");
            }
            System.out.println("Results saved to " + filename);
        } catch (IOException e) {
            System.err.println("Error saving results: " + e.getMessage());
        }
    }
}
