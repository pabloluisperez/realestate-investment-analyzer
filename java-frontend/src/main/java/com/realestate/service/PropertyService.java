package com.realestate.service;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.enterprise.context.ApplicationScoped;
import javax.inject.Inject;
import javax.inject.Named;

import com.realestate.model.Property;
import com.realestate.model.InvestmentOpportunity;

/**
 * Service for retrieving and managing property data
 */
@Named
@ApplicationScoped
public class PropertyService implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @Inject
    private ApiService apiService;
    
    /**
     * Get a list of all cities
     */
    public List<String> getCities() throws Exception {
        return apiService.getCities();
    }
    
    /**
     * Get neighborhoods for a specific city
     */
    public List<String> getNeighborhoods(String city) throws Exception {
        return apiService.getNeighborhoods(city);
    }
    
    /**
     * Get properties with optional filtering
     */
    public List<Property> getProperties(String city, String neighborhood, String propertyType,
            String operationType, Double minPrice, Double maxPrice, Double minSize, Double maxSize,
            Integer minRooms, int limit, int skip) throws Exception {
        
        return apiService.getProperties(city, neighborhood, propertyType, operationType,
                minPrice, maxPrice, minSize, maxSize, minRooms, limit, skip);
    }
    
    /**
     * Get properties with coordinates for map display
     */
    public List<Property> getPropertiesWithCoordinates(String city, String neighborhood,
            String propertyType, String operationType, Double minPrice, Double maxPrice,
            int limit) throws Exception {
        
        return apiService.getPropertiesWithCoordinates(city, neighborhood, propertyType,
                operationType, minPrice, maxPrice, limit);
    }
    
    /**
     * Get a specific property by ID and source
     */
    public Property getPropertyById(String propertyId, String source) throws Exception {
        return apiService.getPropertyById(propertyId, source);
    }
    
    /**
     * Get investment opportunities based on filters
     */
    public List<InvestmentOpportunity> getInvestmentOpportunities(String city, String neighborhood,
            String propertyType, String operationType, Integer minScore, int limit, int skip) throws Exception {
        
        return apiService.getInvestmentOpportunities(city, neighborhood, propertyType,
                operationType, minScore, limit, skip);
    }
    
    /**
     * Get detailed investment analysis for a specific property
     */
    public Map<String, Object> getPropertyAnalysis(String propertyId, String source) throws Exception {
        return apiService.getPropertyAnalysis(propertyId, source);
    }
    
    /**
     * Get the count of properties matching the given filters
     */
    public int getPropertyCount(String city, String neighborhood, String propertyType, String operationType) {
        try {
            List<Property> properties = apiService.getProperties(city, neighborhood, propertyType,
                    operationType, null, null, null, null, null, 1, 0);
            
            // This is not efficient but works for now
            // In a real system, we'd have a dedicated count endpoint
            return properties.size();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }
    
    /**
     * Get the count of investment opportunities matching the given filters
     */
    public int getOpportunityCount(String city, String neighborhood, String propertyType,
            String operationType, Integer minScore) {
        try {
            List<InvestmentOpportunity> opportunities = apiService.getInvestmentOpportunities(
                    city, neighborhood, propertyType, operationType, minScore, 1, 0);
            
            // This is not efficient but works for now
            // In a real system, we'd have a dedicated count endpoint
            return opportunities.size();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }
}
