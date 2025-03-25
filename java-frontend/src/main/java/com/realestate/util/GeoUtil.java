package com.realestate.util;

/**
 * Utility class for geographical calculations
 */
public class GeoUtil {
    
    private static final double EARTH_RADIUS = 6371; // Radius of the earth in km
    
    /**
     * Calculate appropriate zoom level for map bounds
     * 
     * @param minLat Minimum latitude
     * @param maxLat Maximum latitude
     * @param minLng Minimum longitude
     * @param maxLng Maximum longitude
     * @return Appropriate zoom level (1-20)
     */
    public static int calculateZoomLevel(double minLat, double maxLat, double minLng, double maxLng) {
        // Calculate the diagonal distance in kilometers
        double distance = calculateDistance(minLat, minLng, maxLat, maxLng);
        
        // Calculate zoom level based on distance
        // These values are approximate and may need adjustment
        if (distance > 1000) return 5;       // Country level
        if (distance > 500) return 6;
        if (distance > 250) return 7;
        if (distance > 100) return 8;
        if (distance > 50) return 9;
        if (distance > 25) return 10;
        if (distance > 10) return 11;
        if (distance > 5) return 12;
        if (distance > 2) return 13;
        if (distance > 1) return 14;         // City level
        if (distance > 0.5) return 15;       // District level
        if (distance > 0.25) return 16;      // Neighborhood level
        
        return 17;  // Street level
    }
    
    /**
     * Calculate distance between two coordinates using Haversine formula
     * 
     * @param lat1 Latitude of first point
     * @param lng1 Longitude of first point
     * @param lat2 Latitude of second point
     * @param lng2 Longitude of second point
     * @return Distance in kilometers
     */
    public static double calculateDistance(double lat1, double lng1, double lat2, double lng2) {
        double dLat = Math.toRadians(lat2 - lat1);
        double dLng = Math.toRadians(lng2 - lng1);
        
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                  Math.sin(dLng / 2) * Math.sin(dLng / 2);
        
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        double distance = EARTH_RADIUS * c;
        
        return distance;
    }
}
