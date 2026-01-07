import Utility.RandomUtils;
import algorithms.GA;
import problems.TSP;

public class SimpleTest {
    public static void main(String[] args) {
        System.out.println("Starting simple test...");
        
        try {
            TSP tsp = new TSP("bays29.tsp", 1000);
            System.out.println("TSP loaded successfully");
            System.out.println("Number of cities: " + tsp.getNumberOfCities());
            
            TSP.Tour tour = tsp.generateTour();
            System.out.println("Tour generated");
            
            tsp.evaluate(tour);
            System.out.println("Tour evaluated: " + tour.getDistance());
            
            System.out.println("Testing GA with limited generations...");
            GA ga = new GA(10, 0.8, 0.1);  // Population size of 10
            TSP testTsp = new TSP("bays29.tsp", 20);  // Very limited evaluations
            
            System.out.println("Starting GA execution...");
            TSP.Tour best = ga.execute(testTsp);
            System.out.println("GA completed successfully!");
            
            if (best != null) {
                System.out.println("Best tour distance: " + best.getDistance());
            } else {
                System.out.println("No best tour found!");
            }
            System.out.println("Evaluations used: " + testTsp.getNumberOfEvaluations());
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}