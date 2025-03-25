package com.realestate.util;

/**
 * Utilidades para manejo de coordenadas geográficas y cálculos de distancia
 */
public class GeoUtil {
    
    /**
     * Calcula la distancia entre dos puntos geográficos utilizando la fórmula de Haversine
     * 
     * @param lat1 Latitud del punto 1 en grados
     * @param lon1 Longitud del punto 1 en grados
     * @param lat2 Latitud del punto 2 en grados
     * @param lon2 Longitud del punto 2 en grados
     * @return Distancia en kilómetros
     */
    public static double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        final int R = 6371; // Radio de la Tierra en km
        
        double latDistance = Math.toRadians(lat2 - lat1);
        double lonDistance = Math.toRadians(lon2 - lon1);
        
        double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2);
        
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return R * c; // Distancia en km
    }
    
    /**
     * Verifica si unas coordenadas son válidas
     * 
     * @param latitude Latitud a verificar
     * @param longitude Longitud a verificar
     * @return true si las coordenadas son válidas
     */
    public static boolean isValidCoordinates(double latitude, double longitude) {
        return latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
    }
    
    /**
     * Calcula el punto central de un conjunto de coordenadas
     * 
     * @param latitudes Array de latitudes
     * @param longitudes Array de longitudes
     * @return Array con [latitud, longitud] del punto central
     */
    public static double[] calculateCenter(double[] latitudes, double[] longitudes) {
        if (latitudes.length == 0 || longitudes.length == 0) {
            // Coordenadas predeterminadas para Madrid
            return new double[] {40.416775, -3.703790};
        }
        
        double[] result = new double[2];
        double x = 0;
        double y = 0;
        double z = 0;
        
        for (int i = 0; i < latitudes.length; i++) {
            double lat = Math.toRadians(latitudes[i]);
            double lon = Math.toRadians(longitudes[i]);
            
            x += Math.cos(lat) * Math.cos(lon);
            y += Math.cos(lat) * Math.sin(lon);
            z += Math.sin(lat);
        }
        
        x = x / latitudes.length;
        y = y / latitudes.length;
        z = z / latitudes.length;
        
        double centralLongitude = Math.atan2(y, x);
        double centralSquareRoot = Math.sqrt(x * x + y * y);
        double centralLatitude = Math.atan2(z, centralSquareRoot);
        
        result[0] = Math.toDegrees(centralLatitude);
        result[1] = Math.toDegrees(centralLongitude);
        
        return result;
    }
}
