package com.example.pametnipaketnik.tsp;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class TSP {
    
    private static final String TAG = "TSP";
    private static final boolean VERBOSE = false;

    enum DistanceType {EUCLIDEAN, WEIGHTED}

    public class City {
        public int index;
        public double x, y;
    }

    public class Tour {

        double distance;
        int dimension;
        City[] path;

        public Tour(Tour tour) {
            distance = tour.distance;
            dimension = tour.dimension;
            path = tour.path.clone();
        }

        public Tour(int dimension) {
            this.dimension = dimension;
            path = new City[dimension];
            distance = Double.MAX_VALUE;
        }

        public Tour clone() {
            return new Tour(this);
        }

        public double getDistance() {
            return distance;
        }

        public void setDistance(double distance) {
            this.distance = distance;
        }

        public City[] getPath() {
            return path;
        }

        public void setPath(City[] path) {
            this.path = path.clone();
        }

        public void setCity(int index, City city) {
            path[index] = city;
            distance = Double.MAX_VALUE;
        }
    }

    String name;
    City start;
    List<City> cities = new ArrayList<>();
    int numberOfCities;
    double[][] weights;
    DistanceType distanceType = DistanceType.EUCLIDEAN;
    int numberOfEvaluations, maxEvaluations;
    private Context context;

    public TSP(Context context, String path, int maxEvaluations) {
        if (VERBOSE) Log.d(TAG, "TSP constructor started: path=" + path + ", maxEval=" + maxEvaluations);
        this.context = context;
        if (VERBOSE) Log.d(TAG, "About to load data...");
        loadData(path);
        if (VERBOSE) Log.d(TAG, "Data loaded. Cities count: " + cities.size());
        numberOfEvaluations = 0;
        this.maxEvaluations = maxEvaluations;
        if (VERBOSE) Log.d(TAG, "TSP constructor completed");
    }

    public void evaluate(Tour tour) {
        double distance = 0;
        distance += calculateDistance(start, tour.getPath()[0]);
        for (int index = 0; index < numberOfCities; index++) {
            if (index + 1 < numberOfCities)
                distance += calculateDistance(tour.getPath()[index], tour.getPath()[index + 1]);
            else
                distance += calculateDistance(tour.getPath()[index], start);
        }
        tour.setDistance(distance);
        numberOfEvaluations++;
    }

    private double calculateDistance(City from, City to) {
        switch (distanceType) {
            case EUCLIDEAN:
                double dx = from.x - to.x;
                double dy = from.y - to.y;
                return Math.round(Math.sqrt(dx * dx + dy * dy));
            case WEIGHTED:
                return weights[from.index][to.index];
            default:
                return Double.MAX_VALUE;
        }
    }

    public Tour generateTour() {
        Tour tour = new Tour(numberOfCities);
        List<City> availableCities = new ArrayList<>(cities);
        
        for (int i = 0; i < numberOfCities; i++) {
            int randomIndex = RandomUtils.nextInt(availableCities.size());
            tour.setCity(i, availableCities.get(randomIndex));
            availableCities.remove(randomIndex);
        }
        
        return tour;
    }
    
    public Tour createEmptyTour() {
        return new Tour(numberOfCities);
    }

    private void loadData(String path) {
        try {
            if (VERBOSE) Log.d(TAG, "Loading data from: " + path);
            InputStream inputStream;
            
            if (path.startsWith("direct4me_")) {
                java.io.File file = new java.io.File(context.getFilesDir(), path);
                if (file.exists()) {
                    inputStream = new java.io.FileInputStream(file);
                    if (VERBOSE) Log.d(TAG, "Loading from internal storage: " + file.getAbsolutePath());
                } else {
                    Log.e(TAG, "File not found in internal storage: " + path);
                    return;
                }
            } else {
                AssetManager assetManager = context.getAssets();
                inputStream = assetManager.open(path);
                if (VERBOSE) Log.d(TAG, "Loading from assets: " + path);
            }
            
            List<String> lines = new ArrayList<>();
            BufferedReader br = new BufferedReader(new InputStreamReader(inputStream));
            String line = br.readLine();
            int lineCount = 0;
            while (line != null) {
                lines.add(line.trim());
                line = br.readLine();
                lineCount++;
                // quiet
            }
            br.close();
            if (VERBOSE) Log.d(TAG, "File read completed, total lines: " + lines.size());

            if (VERBOSE) Log.d(TAG, "Starting file parsing...");
            parseFile(lines);
            if (VERBOSE) Log.d(TAG, "File parsing completed");
            
            if (!cities.isEmpty()) {
                start = cities.get(0);
                if (VERBOSE) Log.d(TAG, "Start city set: " + start.index);
            } else {
                Log.e(TAG, "No cities loaded!");
            }
        } catch (Exception e) {
            Log.e(TAG, "Error loading data", e);
            e.printStackTrace();
        }
    }

    private void parseFile(List<String> lines) {
        String edgeWeightType = null;
        String edgeWeightFormat = null;
        
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.contains("NAME")) {
                name = line.split(":")[1].trim();
            } else if (line.contains("DIMENSION")) {
                numberOfCities = Integer.parseInt(line.split(":")[1].trim());
            } else if (line.contains("EDGE_WEIGHT_TYPE")) {
                edgeWeightType = line.split(":")[1].trim();
            } else if (line.contains("EDGE_WEIGHT_FORMAT")) {
                edgeWeightFormat = line.split(":")[1].trim();
            } else if (line.equals("NODE_COORD_SECTION")) {
                parseEuclidean2D(lines, i + 1);
                break;
            } else if (line.equals("DISPLAY_DATA_SECTION")) {
                parseDisplayData(lines, i + 1);
                break;
            } else if (line.equals("EDGE_WEIGHT_SECTION")) {
                parseExplicitMatrix(lines, i + 1);
                break;
            }
        }
        
        if ("EXPLICIT".equals(edgeWeightType)) {
            distanceType = DistanceType.WEIGHTED;
        } else if ("EUC_2D".equals(edgeWeightType)) {
            distanceType = DistanceType.EUCLIDEAN;
        }
    }

    private void parseEuclidean2D(List<String> lines, int startLine) {
        cities.clear();
        for (int i = startLine; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.equals("EOF") || line.isEmpty()) break;
            
            String[] parts = line.trim().split("\\s+");
            if (parts.length >= 3) {
                City city = new City();
                city.index = Integer.parseInt(parts[0]) - 1;
                city.x = Double.parseDouble(parts[1]);
                city.y = Double.parseDouble(parts[2]);
                cities.add(city);
            }
        }
    }

    private void parseDisplayData(List<String> lines, int startLine) {
        cities.clear();
        for (int i = startLine; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.equals("EOF") || line.isEmpty()) break;
            
            String[] parts = line.trim().split("\\s+");
            if (parts.length >= 3) {
                City city = new City();
                city.index = Integer.parseInt(parts[0]) - 1;
                city.x = Double.parseDouble(parts[1]);
                city.y = Double.parseDouble(parts[2]);
                cities.add(city);
            }
        }
    }

    private void parseExplicitMatrix(List<String> lines, int startLine) {
        if (VERBOSE) Log.d(TAG, "Parsing explicit matrix for " + numberOfCities + " cities");
        weights = new double[numberOfCities][numberOfCities];
        cities.clear();
        
        for (int i = 0; i < numberOfCities; i++) {
            City city = new City();
            city.index = i;
            city.x = 0;
            city.y = 0;
            cities.add(city);
        }
        
        if (VERBOSE) Log.d(TAG, "Cities created, now parsing matrix weights...");
        int needed = numberOfCities * numberOfCities;
        int filled = 0;
        int row = 0, col = 0;
        for (int i = startLine; i < lines.size() && filled < needed; i++) {
            String line = lines.get(i);
            if (line.equals("EOF") || line.isEmpty()) break;
            String[] parts = line.trim().split("\\s+");
            for (String part : parts) {
                if (part.isEmpty()) continue;
                try {
                    double val = Double.parseDouble(part);
                    weights[row][col] = val;
                    filled++;
                    col++;
                    if (col == numberOfCities) { col = 0; row++; }
                    if (filled >= needed) break;
                } catch (NumberFormatException e) {
                    // stop on section headers or non-numeric tokens
                    if (part.equals("DISPLAY_DATA_SECTION") || part.equals("NODE_COORD_SECTION") || part.equals("EDGE_WEIGHT_SECTION")) {
                        break;
                    }
                    // ignore other non-numeric tokens
                }
            }
        }
        if (filled < needed) {
            Log.w(TAG, "Explicit matrix incomplete: filled=" + filled + " expected=" + needed);
        }
        if (VERBOSE) Log.d(TAG, "Matrix parsing completed");
    }

    public int getMaxEvaluations() {
        return maxEvaluations;
    }

    public int getNumberOfEvaluations() {
        return numberOfEvaluations;
    }
    
    public int getNumberOfCities() {
        return numberOfCities;
    }
    
    public String getName() {
        return name;
    }
}
