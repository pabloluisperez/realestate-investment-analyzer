package com.realestate.beans;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.annotation.PostConstruct;
import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;
import javax.faces.view.ViewScoped;
import javax.inject.Inject;
import javax.inject.Named;

import org.primefaces.event.SlideEndEvent;
import org.primefaces.model.LazyDataModel;

import com.realestate.model.Property;
import com.realestate.model.InvestmentOpportunity;
import com.realestate.service.PropertyService;

/**
 * Backing bean for property-related pages
 */
@Named
@ViewScoped
public class PropertyBean implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @Inject
    private PropertyService propertyService;
    
    // Filter parameters
    private String city;
    private String neighborhood;
    private String propertyType;
    private String operationType = "sale"; // Default to sale
    private Double minPrice;
    private Double maxPrice;
    private Double minSize;
    private Double maxSize;
    private Integer minRooms;
    private Integer minInvestmentScore = 50; // Default min investment score
    
    // Selected property
    private Property selectedProperty;
    private Map<String, Object> propertyAnalysis;
    
    // Lists
    private List<String> cities;
    private List<String> neighborhoods;
    private List<Property> properties;
    private List<InvestmentOpportunity> opportunities;
    
    // Statistics
    private int totalProperties;
    private double averagePrice;
    private double averagePricePerSqm;
    private int opportunityCount;
    
    /**
     * Initialize the bean
     */
    @PostConstruct
    public void init() {
        // Load initial data
        loadCities();
        loadProperties();
        loadOpportunities();
        loadStatistics();
    }
    
    /**
     * Load cities from the API
     */
    public void loadCities() {
        try {
            cities = propertyService.getCities();
        } catch (Exception e) {
            addErrorMessage("Error loading cities: " + e.getMessage());
        }
    }
    
    /**
     * Load neighborhoods for the selected city
     */
    public void loadNeighborhoods() {
        if (city != null && !city.isEmpty()) {
            try {
                neighborhoods = propertyService.getNeighborhoods(city);
            } catch (Exception e) {
                addErrorMessage("Error loading neighborhoods: " + e.getMessage());
            }
        } else {
            neighborhoods = new ArrayList<>();
        }
    }
    
    /**
     * Load properties based on current filters
     */
    public void loadProperties() {
        try {
            properties = propertyService.getProperties(
                    city, neighborhood, propertyType, operationType,
                    minPrice, maxPrice, minSize, maxSize, minRooms, 100, 0);
        } catch (Exception e) {
            addErrorMessage("Error loading properties: " + e.getMessage());
            properties = new ArrayList<>();
        }
    }
    
    /**
     * Load investment opportunities based on current filters
     */
    public void loadOpportunities() {
        try {
            opportunities = propertyService.getInvestmentOpportunities(
                    city, neighborhood, propertyType, operationType, minInvestmentScore, 50, 0);
        } catch (Exception e) {
            addErrorMessage("Error loading investment opportunities: " + e.getMessage());
            opportunities = new ArrayList<>();
        }
    }
    
    /**
     * Load statistics based on current filters
     */
    public void loadStatistics() {
        try {
            // Get total count of properties matching the filter
            totalProperties = propertyService.getPropertyCount(city, neighborhood, propertyType, operationType);
            
            // Calculate average price and price per sqm
            if (properties != null && !properties.isEmpty()) {
                double totalPrice = 0;
                double totalPricePerSqm = 0;
                int priceCount = 0;
                int pricePerSqmCount = 0;
                
                for (Property property : properties) {
                    if (property.getPrice() != null) {
                        totalPrice += property.getPrice();
                        priceCount++;
                    }
                    
                    if (property.getPricePerSqm() != null) {
                        totalPricePerSqm += property.getPricePerSqm();
                        pricePerSqmCount++;
                    }
                }
                
                averagePrice = priceCount > 0 ? totalPrice / priceCount : 0;
                averagePricePerSqm = pricePerSqmCount > 0 ? totalPricePerSqm / pricePerSqmCount : 0;
            } else {
                averagePrice = 0;
                averagePricePerSqm = 0;
            }
            
            // Get count of investment opportunities
            opportunityCount = propertyService.getOpportunityCount(city, neighborhood, propertyType, operationType, minInvestmentScore);
        } catch (Exception e) {
            addErrorMessage("Error loading statistics: " + e.getMessage());
        }
    }
    
    /**
     * Apply filters and reload data
     */
    public void applyFilters() {
        loadProperties();
        loadOpportunities();
        loadStatistics();
    }
    
    /**
     * Reset all filters
     */
    public void resetFilters() {
        city = null;
        neighborhood = null;
        propertyType = null;
        operationType = "sale";
        minPrice = null;
        maxPrice = null;
        minSize = null;
        maxSize = null;
        minRooms = null;
        minInvestmentScore = 50;
        
        loadProperties();
        loadOpportunities();
        loadStatistics();
    }
    
    /**
     * Load detailed property data for the selected property
     */
    public void loadPropertyDetails(String propertyId, String source) {
        try {
            selectedProperty = propertyService.getPropertyById(propertyId, source);
            propertyAnalysis = propertyService.getPropertyAnalysis(propertyId, source);
        } catch (Exception e) {
            addErrorMessage("Error loading property details: " + e.getMessage());
        }
    }
    
    /**
     * Handle investment score slider change
     */
    public void onInvestmentScoreChange(SlideEndEvent event) {
        minInvestmentScore = event.getValue();
        loadOpportunities();
        loadStatistics();
    }
    
    /**
     * Get CSS class for investment score
     */
    public String getInvestmentScoreClass(Number score) {
        if (score == null) {
            return "";
        }
        
        int scoreValue = score.intValue();
        if (scoreValue >= 70) {
            return "score-high";
        } else if (scoreValue >= 50) {
            return "score-medium";
        } else {
            return "score-low";
        }
    }
    
    /**
     * Add an error message to be displayed in the UI
     */
    private void addErrorMessage(String message) {
        FacesContext.getCurrentInstance().addMessage(null, 
                new FacesMessage(FacesMessage.SEVERITY_ERROR, "Error", message));
    }
    
    // Getters and setters
    
    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
        this.neighborhood = null; // Reset neighborhood when city changes
        loadNeighborhoods();
    }

    public String getNeighborhood() {
        return neighborhood;
    }

    public void setNeighborhood(String neighborhood) {
        this.neighborhood = neighborhood;
    }

    public String getPropertyType() {
        return propertyType;
    }

    public void setPropertyType(String propertyType) {
        this.propertyType = propertyType;
    }

    public String getOperationType() {
        return operationType;
    }

    public void setOperationType(String operationType) {
        this.operationType = operationType;
    }

    public Double getMinPrice() {
        return minPrice;
    }

    public void setMinPrice(Double minPrice) {
        this.minPrice = minPrice;
    }

    public Double getMaxPrice() {
        return maxPrice;
    }

    public void setMaxPrice(Double maxPrice) {
        this.maxPrice = maxPrice;
    }

    public Double getMinSize() {
        return minSize;
    }

    public void setMinSize(Double minSize) {
        this.minSize = minSize;
    }

    public Double getMaxSize() {
        return maxSize;
    }

    public void setMaxSize(Double maxSize) {
        this.maxSize = maxSize;
    }

    public Integer getMinRooms() {
        return minRooms;
    }

    public void setMinRooms(Integer minRooms) {
        this.minRooms = minRooms;
    }

    public Integer getMinInvestmentScore() {
        return minInvestmentScore;
    }

    public void setMinInvestmentScore(Integer minInvestmentScore) {
        this.minInvestmentScore = minInvestmentScore;
    }

    public Property getSelectedProperty() {
        return selectedProperty;
    }

    public void setSelectedProperty(Property selectedProperty) {
        this.selectedProperty = selectedProperty;
    }

    public Map<String, Object> getPropertyAnalysis() {
        return propertyAnalysis;
    }

    public void setPropertyAnalysis(Map<String, Object> propertyAnalysis) {
        this.propertyAnalysis = propertyAnalysis;
    }

    public List<String> getCities() {
        return cities;
    }

    public List<String> getNeighborhoods() {
        return neighborhoods;
    }

    public List<Property> getProperties() {
        return properties;
    }

    public List<InvestmentOpportunity> getOpportunities() {
        return opportunities;
    }

    public int getTotalProperties() {
        return totalProperties;
    }

    public double getAveragePrice() {
        return averagePrice;
    }

    public double getAveragePricePerSqm() {
        return averagePricePerSqm;
    }

    public int getOpportunityCount() {
        return opportunityCount;
    }
}
