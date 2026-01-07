package algorithms;

import Utility.RandomUtils;
import problems.TSP;

import java.util.ArrayList;

public class GA {

    int popSize;
    double cr;
    double pm;

    ArrayList<TSP.Tour> population;
    ArrayList<TSP.Tour> offspring;

    public GA(int popSize, double cr, double pm) {
        this.popSize = popSize;
        this.cr = cr;
        this.pm = pm;
    }

    public TSP.Tour execute(TSP problem) {
        population = new ArrayList<>();
        offspring = new ArrayList<>();
        TSP.Tour best = null;

        for (int i = 0; i < popSize; i++) {
            TSP.Tour newTour = problem.generateTour();
            problem.evaluate(newTour);
            population.add(newTour);
            if (best == null || newTour.getDistance() < best.getDistance()) {
                best = newTour.clone();
            }
        }

        while (problem.getNumberOfEvaluations() < problem.getMaxEvaluations()) {
            TSP.Tour currentBest = null;
            for (TSP.Tour individual : population) {
                if (currentBest == null || individual.getDistance() < currentBest.getDistance()) {
                    currentBest = individual;
                }
            }
            offspring.add(currentBest.clone());
            
            for (int i = 1; i < popSize && problem.getNumberOfEvaluations() < problem.getMaxEvaluations(); i++) {
                TSP.Tour parent1 = tournamentSelection();
                TSP.Tour parent2 = tournamentSelection();
                
                while (parent1 == parent2 && population.size() > 1) {
                    parent2 = tournamentSelection();
                }

                TSP.Tour child;
                if (RandomUtils.nextDouble() < cr) {
                    TSP.Tour[] children = pmx(parent1, parent2, problem);
                    child = children[0];
                } else {
                    child = parent1.clone();
                }
                
                if (RandomUtils.nextDouble() < pm) {
                    swapMutation(child);
                }
                
                offspring.add(child);
            }

            for (TSP.Tour off : offspring) {
                if (off.getDistance() == Double.MAX_VALUE && problem.getNumberOfEvaluations() < problem.getMaxEvaluations()) {
                    problem.evaluate(off);
                    if (off.getDistance() < best.getDistance()) {
                        best = off.clone();
                    }
                }
            }

            population = new ArrayList<>(offspring);
            offspring.clear();
        }
        return best;
    }

    private void swapMutation(TSP.Tour off) {
        TSP.City[] path = off.getPath();
        int length = path.length;
        
        int index1 = RandomUtils.nextInt(length);
        int index2 = RandomUtils.nextInt(length);
        
        while (index1 == index2) {
            index2 = RandomUtils.nextInt(length);
        }
        
        TSP.City temp = path[index1];
        path[index1] = path[index2];
        path[index2] = temp;
        
        off.setDistance(Double.MAX_VALUE);
    }

    private TSP.Tour[] pmx(TSP.Tour parent1, TSP.Tour parent2, TSP problem) {
        int length = parent1.getPath().length;
        TSP.Tour child1 = problem.createEmptyTour();
        TSP.Tour child2 = problem.createEmptyTour();
        
        TSP.City[] p1Path = parent1.getPath();
        TSP.City[] p2Path = parent2.getPath();
        TSP.City[] c1Path = new TSP.City[length];
        TSP.City[] c2Path = new TSP.City[length];
        
        int crossPoint1 = RandomUtils.nextInt(length);
        int crossPoint2 = RandomUtils.nextInt(length);
        
        if (crossPoint1 > crossPoint2) {
            int temp = crossPoint1;
            crossPoint1 = crossPoint2;
            crossPoint2 = temp;
        }
        
        for (int i = crossPoint1; i <= crossPoint2; i++) {
            c1Path[i] = p2Path[i];
            c2Path[i] = p1Path[i];
        }
        
        for (int i = 0; i < length; i++) {
            if (i < crossPoint1 || i > crossPoint2) {
                TSP.City city1ToPlace = p1Path[i];
                TSP.City city2ToPlace = p2Path[i];
                
                if (!contains(c1Path, city1ToPlace, crossPoint1, crossPoint2)) {
                    c1Path[i] = city1ToPlace;
                } else {
                    TSP.City mappedCity = city1ToPlace;
                    while (contains(c1Path, mappedCity, crossPoint1, crossPoint2)) {
                        int mappedIndex = findIndex(p1Path, mappedCity);
                        if (mappedIndex == -1) {
                            break;
                        }
                        mappedCity = p2Path[mappedIndex];
                    }
                    c1Path[i] = mappedCity;
                }
                
                if (!contains(c2Path, city2ToPlace, crossPoint1, crossPoint2)) {
                    c2Path[i] = city2ToPlace;
                } else {
                    TSP.City mappedCity = city2ToPlace;
                    while (contains(c2Path, mappedCity, crossPoint1, crossPoint2)) {
                        int mappedIndex = findIndex(p2Path, mappedCity);
                        if (mappedIndex == -1) {
                            break;
                        }
                        mappedCity = p1Path[mappedIndex];
                    }
                    c2Path[i] = mappedCity;
                }
            }
        }
        
        child1.setPath(c1Path);
        child2.setPath(c2Path);
        
        return new TSP.Tour[]{child1, child2};
    }
    
    private boolean contains(TSP.City[] path, TSP.City city, int start, int end) {
        for (int i = start; i <= end; i++) {
            if (path[i] != null && path[i].index == city.index) {
                return true;
            }
        }
        return false;
    }
    
    private int findIndex(TSP.City[] path, TSP.City city) {
        for (int i = 0; i < path.length; i++) {
            if (path[i].index == city.index) {
                return i;
            }
        }
        return -1;
    }

    private TSP.Tour tournamentSelection() {
        int index1 = RandomUtils.nextInt(population.size());
        int index2 = RandomUtils.nextInt(population.size());
        
        while (index1 == index2) {
            index2 = RandomUtils.nextInt(population.size());
        }
        
        TSP.Tour individual1 = population.get(index1);
        TSP.Tour individual2 = population.get(index2);
        
        return (individual1.getDistance() < individual2.getDistance()) ? individual1 : individual2;
    }
}
