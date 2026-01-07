import java.io.*;
import java.nio.file.*;
import java.util.*;


class TestRandomUtils {
    private static long seed = 123L;
    private static Random random = new Random(seed);
    
    public static void setSeed(long newSeed) {
        seed = newSeed;
        random = new Random(seed);
    }
    
    public static double nextDouble() { return random.nextDouble(); }
    public static int nextInt(int bound) { return random.nextInt(bound); }
    
    public static void setSeedFromTime() {
        setSeed(System.currentTimeMillis());
    }
}

class City {
    public int index;
    public double x, y;
    
    public City(int index, double x, double y) {
        this.index = index;
        this.x = x;
        this.y = y;
    }
}

class Tour {
    public double distance = Double.MAX_VALUE;
    public int dimension;
    public City[] path;
    
    public Tour(int dimension) {
        this.dimension = dimension;
        this.path = new City[dimension];
    }
    
    public Tour clone() {
        Tour newTour = new Tour(dimension);
        newTour.distance = distance;
        newTour.path = path.clone();
        return newTour;
    }
}

class TSPProblem {
    private List<City> cities = new ArrayList<>();
    private double[][] weights;
    private String distanceType = "EUCLIDEAN";
    private String instanceName;
    public int numberOfEvaluations = 0;
    public int maxEvaluations = 0;
    
    public int getNumberOfCities() { return cities.size(); }
    public String getName() { return instanceName; }
    
    public TSPProblem(String instanceName) throws IOException {
        this.instanceName = instanceName;
        loadData();
        maxEvaluations = 1000 * getNumberOfCities();
        System.out.println("TSP Problem loaded: " + instanceName + ", Cities: " + getNumberOfCities() + ", MaxFes: " + maxEvaluations);
    }
    
    private void loadData() throws IOException {
        String resourcePath = "/home/matic/Desktop/pametni-paketnik/PJ/EVOLUCIJSKI/TSP/" + instanceName;
        List<String> lines = Files.readAllLines(Paths.get(resourcePath));
        
        boolean readingNodes = false;
        boolean readingWeights = false;
        int dimension = 0;
        String edgeWeightFormat = "";
        
        for (String line : lines) {
            String trimmed = line.trim();
            
            if (trimmed.startsWith("DIMENSION")) {
                dimension = Integer.parseInt(trimmed.split(":")[1].trim());
                System.out.println("Dimension: " + dimension);
            } else if (trimmed.startsWith("EDGE_WEIGHT_TYPE")) {
                distanceType = trimmed.split(":")[1].trim();
                System.out.println("Distance type: " + distanceType);
            } else if (trimmed.startsWith("EDGE_WEIGHT_FORMAT")) {
                edgeWeightFormat = trimmed.split(":")[1].trim();
                System.out.println("Weight format: " + edgeWeightFormat);
            } else if (trimmed.equals("NODE_COORD_SECTION")) {
                readingNodes = true;
                continue;
            } else if (trimmed.equals("EDGE_WEIGHT_SECTION")) {
                readingWeights = true;
                weights = new double[dimension][dimension];
                continue;
            } else if (trimmed.equals("EOF")) {
                break;
            } else if (readingNodes && !trimmed.isEmpty()) {
                String[] parts = trimmed.split("\\s+");
                if (parts.length >= 3) {
                    int index = Integer.parseInt(parts[0]) - 1;
                    double x = Double.parseDouble(parts[1]);
                    double y = Double.parseDouble(parts[2]);
                    cities.add(new City(index, x, y));
                }
            } else if (readingWeights && !trimmed.isEmpty() && weights != null) {
                String[] parts = trimmed.split("\\s+");
                for (String part : parts) {
                    if (!part.isEmpty()) {
                        try {
                            weightValues.add(Double.parseDouble(part));
                        } catch (NumberFormatException e) {
                        }
                    }
                }
            }
        }
        
        if (weights != null && !weightValues.isEmpty()) {
            int valueIndex = 0;
            for (int i = 0; i < dimension && valueIndex < weightValues.size(); i++) {
                for (int j = 0; j < dimension && valueIndex < weightValues.size(); j++) {
                    weights[i][j] = weightValues.get(valueIndex++);
                }
            }
        }
        
        if (cities.isEmpty() && dimension > 0) {
            for (int i = 0; i < dimension; i++) {
                cities.add(new City(i, 0, 0));
            }
        }
        
        System.out.println("Loaded TSP: " + instanceName + ", type: " + distanceType + ", cities: " + cities.size());
    }
    
    private List<Double> weightValues = new ArrayList<>();
    
    public Tour generateTour() {
        List<City> shuffled = new ArrayList<>(cities);
        Collections.shuffle(shuffled, new Random(TestRandomUtils.nextInt(Integer.MAX_VALUE)));
        
        Tour tour = new Tour(getNumberOfCities());
        for (int i = 0; i < shuffled.size(); i++) {
            tour.path[i] = shuffled.get(i);
        }
        return tour;
    }
    
    public Tour createEmptyTour() {
        return new Tour(getNumberOfCities());
    }
    
    public void evaluate(Tour tour) {
        double distance = 0.0;
        City[] path = tour.path;
        
        for (int i = 0; i < path.length; i++) {
            City from = path[i];
            City to = path[(i + 1) % path.length];
            distance += calculateDistance(from, to);
        }
        
        tour.distance = distance;
        numberOfEvaluations++;
    }
    
    private double calculateDistance(City city1, City city2) {
        if ("EXPLICIT".equals(distanceType)) {
            return weights != null ? weights[city1.index][city2.index] : Double.MAX_VALUE;
        } else {
            double dx = city1.x - city2.x;
            double dy = city1.y - city2.y;
            return Math.sqrt(dx * dx + dy * dy);
        }
    }
}

class SimpleGA {
    private int popSize;
    private double crossoverRate;
    private double mutationRate;
    
    public SimpleGA(int popSize, double crossoverRate, double mutationRate) {
        this.popSize = popSize;
        this.crossoverRate = crossoverRate;
        this.mutationRate = mutationRate;
    }
    
    public Tour execute(TSPProblem problem) {
        List<Tour> population = new ArrayList<>();
        Tour best = null;
        int generation = 0;
        
        for (int i = 0; i < popSize; i++) {
            Tour tour = problem.generateTour();
            problem.evaluate(tour);
            population.add(tour);
            if (best == null || tour.distance < best.distance) {
                best = tour.clone();
            }
        }
        
        System.out.println("Initial best: " + (int)best.distance);
        
        while (problem.numberOfEvaluations < problem.maxEvaluations) {
            generation++;
            List<Tour> offspring = new ArrayList<>();
            
            Tour currentBest = null;
            for (Tour individual : population) {
                if (currentBest == null || individual.distance < currentBest.distance) {
                    currentBest = individual;
                }
            }
            if (currentBest != null) {
                offspring.add(currentBest.clone());
            }
            
            while (offspring.size() < popSize && problem.numberOfEvaluations < problem.maxEvaluations) {
                Tour parent1 = tournamentSelection(population);
                Tour parent2 = tournamentSelection(population);
                
                Tour child;
                if (TestRandomUtils.nextDouble() < crossoverRate) {
                    child = pmxCrossover(parent1, parent2, problem);
                } else {
                    child = parent1.clone();
                }
                
                if (TestRandomUtils.nextDouble() < mutationRate) {
                    swapMutation(child);
                }
                
                problem.evaluate(child);
                offspring.add(child);
                
                if (child.distance < best.distance) {
                    best = child.clone();
                }
            }
            
            population = offspring;
            
            if (generation % 50 == 0) {
                System.out.println("Generation " + generation + ": best = " + (int)best.distance + 
                    ", evals = " + problem.numberOfEvaluations + "/" + problem.maxEvaluations);
            }
        }
        
        return best;
    }
    
    private Tour tournamentSelection(List<Tour> population) {
        int idx1 = TestRandomUtils.nextInt(population.size());
        int idx2 = TestRandomUtils.nextInt(population.size());
        
        return population.get(idx1).distance < population.get(idx2).distance ? 
               population.get(idx1) : population.get(idx2);
    }
    
    private Tour pmxCrossover(Tour parent1, Tour parent2, TSPProblem problem) {
        int length = parent1.dimension;
        Tour child = problem.createEmptyTour();
        City[] childPath = new City[length];
        
        int crossPoint1 = TestRandomUtils.nextInt(length);
        int crossPoint2 = TestRandomUtils.nextInt(length);
        
        int start = Math.min(crossPoint1, crossPoint2);
        int end = Math.max(crossPoint1, crossPoint2);
        
        for (int i = start; i <= end; i++) {
            childPath[i] = parent2.path[i];
        }
        
        Set<Integer> used = new HashSet<>();
        for (int i = start; i <= end; i++) {
            used.add(childPath[i].index);
        }
        
        int fillIndex = 0;
        for (int i = 0; i < length; i++) {
            if (i < start || i > end) {
                while (fillIndex < length && used.contains(parent1.path[fillIndex].index)) {
                    fillIndex++;
                }
                if (fillIndex < length) {
                    childPath[i] = parent1.path[fillIndex];
                    used.add(parent1.path[fillIndex].index);
                    fillIndex++;
                }
            }
        }
        
        child.path = childPath;
        return child;
    }
    
    private void swapMutation(Tour tour) {
        City[] path = tour.path;
        int idx1 = TestRandomUtils.nextInt(path.length);
        int idx2 = TestRandomUtils.nextInt(path.length);
        
        while (idx1 == idx2) {
            idx2 = TestRandomUtils.nextInt(path.length);
        }
        
        City temp = path[idx1];
        path[idx1] = path[idx2];
        path[idx2] = temp;
        
        tour.distance = Double.MAX_VALUE;
    }
}

public class TSPBenchmarkTestFixed {
    
    public static void main(String[] args) {
        String[] instances = {"bays29.tsp", "eil101.tsp", "a280.tsp", "pr1002.tsp", "dca1389.tsp"};
        String teamName = "Postar";
        int runs = 30;
        int popSize = 100;
        double crossoverRate = 0.8;
        double mutationRate = 0.1;
        
        File resultsDir = new File("/home/matic/Desktop/pametni-paketnik/PJ/rezultati");
        if (!resultsDir.exists()) {
            resultsDir.mkdirs();
        }
        
        System.out.println("TSP BENCHMARK TEST - FIXED VERSION");
        System.out.println("===================================");
        System.out.println("Parameters: runs=" + runs + ", pop=" + popSize + ", cr=" + crossoverRate + ", pm=" + mutationRate);
        System.out.println("TSP files from: /home/matic/Desktop/pametni-paketnik/PJ/EVOLUCIJSKI/TSP/");
        System.out.println("Results will be saved to: " + resultsDir.getAbsolutePath());
        System.out.println();
        
        for (int index = 0; index < instances.length; index++) {
            String instance = instances[index];
            System.out.println("=== INSTANCE " + (index + 1) + "/5: " + instance + " ===");
            
            try {
                TestRandomUtils.setSeed(123);
                List<Double> results = new ArrayList<>();
                
                TSPProblem problem = new TSPProblem(instance);
                SimpleGA ga = new SimpleGA(popSize, crossoverRate, mutationRate);
                
                for (int run = 1; run <= runs; run++) {
                    System.out.println("Run " + run + "/" + runs + "...");
                    
                    Tour best = ga.execute(problem);
                    if (best != null) {
                        results.add(best.distance);
                        System.out.println("  Distance: " + (int)best.distance);
                    }
                    
                        problem.numberOfEvaluations = 0;
                }
                
                if (!results.isEmpty()) {
                    double best = Collections.min(results);
                    double average = results.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                    
                    System.out.println("Completed: Best=" + (int)best + ", Average=" + (int)average);
                    
                    String instanceName = instance.replace(".tsp", "");
                    String fileName = teamName + "_" + instanceName + ".txt";
                    File file = new File(resultsDir, fileName);
                    
                    try (PrintWriter writer = new PrintWriter(file)) {
                        for (Double result : results) {
                            writer.println((int)result.doubleValue());
                        }
                    }
                    
                    System.out.println("Results saved to: " + file.getAbsolutePath());
                } else {
                    System.out.println("ERROR: No results for " + instance);
                }
                
            } catch (Exception e) {
                System.out.println("ERROR processing " + instance + ": " + e.getMessage());
                e.printStackTrace();
            }
            
            System.out.println();
        }
        
        TestRandomUtils.setSeedFromTime();
        
        System.out.println("=== ALL TESTS COMPLETED ===");
        System.out.println("Generated files in " + resultsDir.getAbsolutePath() + ":");
        for (String instance : instances) {
            String instanceName = instance.replace(".tsp", "");
            System.out.println("• " + teamName + "_" + instanceName + ".txt");
        }
    }
}