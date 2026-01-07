package problems;

import Utility.RandomUtils;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class TSP {

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


    public TSP(String path, int maxEvaluations) {
        loadData(path);
        numberOfEvaluations = 0;
        this.maxEvaluations = maxEvaluations;
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
        InputStream inputStream = TSP.class.getClassLoader().getResourceAsStream(path);
        if(inputStream == null) {
            System.err.println("File "+path+" not found!");
            return;
        }

        List<String> lines = new ArrayList<>();
        try(BufferedReader br = new BufferedReader(new InputStreamReader(inputStream))) {
            String line = br.readLine();
            while (line != null) {
                lines.add(line.trim());
                line = br.readLine();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        parseFile(lines);
        
        start = cities.get(0);
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

    private void parseExplicitMatrix(List<String> lines, int startLine) {
        weights = new double[numberOfCities][numberOfCities];
        cities.clear();
        
        for (int i = 0; i < numberOfCities; i++) {
            City city = new City();
            city.index = i;
            city.x = 0;
            city.y = 0;
            cities.add(city);
        }
        
        List<Integer> allWeights = new ArrayList<>();
        for (int i = startLine; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.equals("EOF") || line.isEmpty()) break;
            
            String[] parts = line.trim().split("\\s+");
            for (String part : parts) {
                try {
                    allWeights.add(Integer.parseInt(part));
                } catch (NumberFormatException e) {
                }
            }
        }
        
        int idx = 0;
        for (int i = 0; i < numberOfCities; i++) {
            for (int j = 0; j < numberOfCities; j++) {
                if (idx < allWeights.size()) {
                    weights[i][j] = allWeights.get(idx++);
                }
            }
        }
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
}
