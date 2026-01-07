package com.example.pametnipaketnik.tsp;

import java.util.Random;

public class RandomUtils {

    private RandomUtils() {
    }

    private static long seed = 123;
    private static final Random random = new Random(seed);

    public static void setSeed(long seed) {
        RandomUtils.seed = seed;
        random.setSeed(seed);
    }

    public static void setSeedFromTime() {
        RandomUtils.seed = System.currentTimeMillis();
        random.setSeed(seed);
    }

    public static long getSeed() {
        return seed;
    }

    public static double nextDouble() {
        return random.nextDouble();
    }

    public static int nextInt(int upperBound) {
        return random.nextInt(upperBound);
    }

    public static int nextInt(int lowerBound, int upperBound) {
        return lowerBound + random.nextInt(upperBound - lowerBound);
    }
}