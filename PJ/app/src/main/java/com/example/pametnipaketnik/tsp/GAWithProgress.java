package com.example.pametnipaketnik.tsp;

import android.util.Log;
import java.util.ArrayList;

public class GAWithProgress extends GA {

    private static final String TAG = "GAWithProgress";
    private static final boolean VERBOSE = false;
    
    public interface ProgressListener {
        void onGenerationComplete(int generation, int evaluations, int maxEvaluations, double bestDistance);
    }
    
    private ProgressListener progressListener;
    
    public GAWithProgress(int popSize, double cr, double pm, ProgressListener listener) {
        super(popSize, cr, pm);
        this.progressListener = listener;
    }
    
    @Override
    public TSP.Tour execute(TSP problem) {
        if (VERBOSE) Log.d(TAG, "GA execution started");
        population = new ArrayList<>();
        offspring = new ArrayList<>();
        TSP.Tour best = null;
        int generation = 0;

        if (VERBOSE) Log.d(TAG, "Creating initial population of size: " + popSize);
        for (int i = 0; i < popSize; i++) {
            if (VERBOSE && i % 10 == 0) Log.d(TAG, "Creating individual " + i + "/" + popSize);
            TSP.Tour newTour = problem.generateTour();
            problem.evaluate(newTour);
            population.add(newTour);
            if (best == null || newTour.getDistance() < best.getDistance()) {
                best = newTour.clone();
            }
        }
        if (VERBOSE) Log.d(TAG, "Initial population created. Best distance: " + best.getDistance());
        
        if (progressListener != null) {
            progressListener.onGenerationComplete(0, problem.getNumberOfEvaluations(), 
                problem.getMaxEvaluations(), best.getDistance());
        }

        if (VERBOSE) Log.d(TAG, "Starting main evolution loop. Max evaluations: " + problem.getMaxEvaluations());
        
        long startTime = System.currentTimeMillis();
        long maxRunTime = 5 * 60 * 1000;
        int maxGenerations = 1000;
        
        while (problem.getNumberOfEvaluations() < problem.getMaxEvaluations() && generation < maxGenerations) {
            long currentTime = System.currentTimeMillis();
            if (currentTime - startTime > maxRunTime) {
                Log.w(TAG, "Algorithm timeout after " + (currentTime - startTime) + "ms, terminating early");
                break;
            }
            generation++;
            if (VERBOSE && generation % 50 == 0) {
                Log.d(TAG, "=== Generation " + generation + " === evals=" + problem.getNumberOfEvaluations());
            }
            
            offspring.clear();
            
            TSP.Tour currentBest = null;
            for (TSP.Tour individual : population) {
                if (currentBest == null || individual.getDistance() < currentBest.getDistance()) {
                    currentBest = individual;
                }
            }
            offspring.add(currentBest.clone());
            if (VERBOSE) Log.d(TAG, "Elite added, current best distance: " + currentBest.getDistance());
            
            for (int i = 1; i < popSize && problem.getNumberOfEvaluations() < problem.getMaxEvaluations(); i++) {
                try {
                    if (problem.getNumberOfEvaluations() >= problem.getMaxEvaluations()) {
                        if (VERBOSE) Log.d(TAG, "Breaking offspring creation - max evaluations reached");
                        break;
                    }
                    
                    TSP.Tour parent1 = tournamentSelection();
                    TSP.Tour parent2 = tournamentSelection();
                    
                    int attempts = 0;
                    int maxAttempts = Math.min(5, population.size());
                    while (parent1 == parent2 && population.size() > 1 && attempts < maxAttempts) {
                        parent2 = tournamentSelection();
                        attempts++;
                        if (attempts >= maxAttempts) {
                            if (VERBOSE) Log.d(TAG, "Max parent selection attempts reached, using different selection");
                            int idx = RandomUtils.nextInt(population.size());
                            parent2 = population.get(idx);
                            break;
                        }
                    }

                    TSP.Tour child;
                    if (RandomUtils.nextDouble() < cr) {
                        try {
                            TSP.Tour[] children = pmx(parent1, parent2, problem);
                            child = children[0];
                        } catch (Exception e) {
                            if (VERBOSE) Log.w(TAG, "PMX crossover failed, falling back to parent1: " + e.getMessage());
                            child = parent1.clone();
                        }
                    } else {
                        child = parent1.clone();
                    }
                    
                    if (RandomUtils.nextDouble() < pm) {
                        try {
                            swapMutation(child);
                        } catch (Exception e) {
                            if (VERBOSE) Log.w(TAG, "Mutation failed: " + e.getMessage());
                        }
                    }
                    
                    offspring.add(child);
                    
                } catch (Exception e) {
                    Log.e(TAG, "Critical error creating offspring " + i + ": " + e.getMessage());
                    e.printStackTrace();
                    if (offspring.size() < popSize - 1) {
                        offspring.add(currentBest.clone());
                    }
                }
            }
            
            while (offspring.size() < popSize) {
                if (VERBOSE) Log.w(TAG, "Offspring size only " + offspring.size() + ", adding elite copy");
                offspring.add(currentBest.clone());
            }

            
            int evaluated = 0;
            int alreadyEvaluated = 0;
            for (int idx = 0; idx < offspring.size(); idx++) {
                TSP.Tour off = offspring.get(idx);
                if (off.getDistance() == Double.MAX_VALUE && problem.getNumberOfEvaluations() < problem.getMaxEvaluations()) {
                    try {
                        problem.evaluate(off);
                        evaluated++;
                        if (off.getDistance() < best.getDistance()) {
                            best = off.clone();
                            if (VERBOSE) Log.d(TAG, "New best found: " + best.getDistance());
                        }
                    } catch (Exception e) {
                        if (VERBOSE) Log.e(TAG, "Evaluation failed for offspring " + idx + ": " + e.getMessage());
                        off.setDistance(Double.MAX_VALUE);
                    }
                } else {
                    alreadyEvaluated++;
                }
            }

            population = new ArrayList<>(offspring);
            
            if (progressListener != null) {
                try {
                    progressListener.onGenerationComplete(generation, problem.getNumberOfEvaluations(),
                        problem.getMaxEvaluations(), best.getDistance());
                } catch (Exception e) {
                    Log.e(TAG, "Progress listener failed: " + e.getMessage());
                    e.printStackTrace();
                }
            }
            
            if (generation % 25 == 0 || generation <= 5) {
                Log.d(TAG, "Generation " + generation + " completed. Evals: " + problem.getNumberOfEvaluations() + "/" + problem.getMaxEvaluations() + ", Best: " + best.getDistance());
            }
        }
        if (VERBOSE) Log.d(TAG, "Evolution completed after " + generation + " generations");
        return best;
    }
    
    private TSP.Tour orderCrossover(TSP.Tour parent1, TSP.Tour parent2, TSP problem) {
        int length = parent1.getPath().length;
        TSP.Tour child = problem.createEmptyTour();
        TSP.City[] childPath = new TSP.City[length];
        boolean[] used = new boolean[length];
        
        int start = RandomUtils.nextInt(length);
        int end = RandomUtils.nextInt(length);
        if (start > end) {
            int temp = start;
            start = end;
            end = temp;
        }
        
        for (int i = start; i <= end; i++) {
            childPath[i] = parent1.getPath()[i];
            used[parent1.getPath()[i].index] = true;
        }
        
        int pos = (end + 1) % length;
        for (int i = 0; i < length; i++) {
            int p2Pos = (end + 1 + i) % length;
            TSP.City city = parent2.getPath()[p2Pos];
            if (!used[city.index]) {
                childPath[pos] = city;
                pos = (pos + 1) % length;
            }
        }
        
        child.setPath(childPath);
        return child;
    }
}
