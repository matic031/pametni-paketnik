import Utility.RandomUtils;
import algorithms.GA;
import problems.TSP;

public class TestPMX {
    public static void main(String[] args) {
        TSP tsp = new TSP("bays29.tsp", 100);
        
        TSP.Tour parent1 = tsp.generateTour();
        tsp.evaluate(parent1);
        System.out.println("Parent 1 distance: " + parent1.getDistance());
        
        TSP.Tour parent2 = tsp.generateTour();
        tsp.evaluate(parent2);
        System.out.println("Parent 2 distance: " + parent2.getDistance());
        
        GA ga = new GA(10, 0.8, 0.1);
        System.out.println("Testing PMX...");
        
        try {
            // This should test if PMX is causing the infinite loop
            java.lang.reflect.Method pmxMethod = GA.class.getDeclaredMethod("pmx", TSP.Tour.class, TSP.Tour.class, TSP.class);
            pmxMethod.setAccessible(true);
            TSP.Tour[] children = (TSP.Tour[]) pmxMethod.invoke(ga, parent1, parent2, tsp);
            
            System.out.println("PMX completed successfully");
            if (children != null && children.length >= 2) {
                tsp.evaluate(children[0]);
                tsp.evaluate(children[1]);
                System.out.println("Child 1 distance: " + children[0].getDistance());
                System.out.println("Child 2 distance: " + children[1].getDistance());
            }
        } catch (Exception e) {
            System.err.println("PMX failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}