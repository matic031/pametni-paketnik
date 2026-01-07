import Utility.RandomUtils;
import algorithms.GA;
import problems.TSP;

public class QuickTest {
    public static void main(String[] args) {
        System.out.println("Quick test with very limited evaluations");
        
        TSP tsp = new TSP("bays29.tsp", 200);
        GA ga = new GA(10, 0.8, 0.1);
        
        TSP.Tour bestTour = ga.execute(tsp);
        
        if (bestTour != null) {
            System.out.println("Best distance: " + bestTour.getDistance());
            System.out.println("Evaluations used: " + tsp.getNumberOfEvaluations());
        } else {
            System.out.println("No solution found");
        }
    }
}