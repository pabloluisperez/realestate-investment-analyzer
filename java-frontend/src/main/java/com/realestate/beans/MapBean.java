package com.realestate.beans;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import javax.annotation.PostConstruct;
import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;
import javax.faces.view.ViewScoped;
import javax.inject.Inject;
import javax.inject.Named;

import org.primefaces.event.map.OverlaySelectEvent;
import org.primefaces.model.map.DefaultMapModel;
import org.primefaces.model.map.LatLng;
import org.primefaces.model.map.MapModel;
import org.primefaces.model.map.Marker;

import com.realestate.model.Property;
import com.realestate.service.PropertyService;
import com.realestate.util.GeoUtil;

/**
 * Backing bean for the map view
 */
@Named
@ViewScoped
public class MapBean implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @Inject
    private PropertyService propertyService;
    
    private MapModel mapModel;
    private String center = "40.416775, -3.703790"; // Default center (Madrid)
    private int zoom = 7; // Default zoom level
    
    // Filter parameters
    private String city;
    private String neighborhood;
    private String propertyType;
    private String operationType = "sale"; // Default to sale
    private Double minPrice;
    private Double maxPrice;
    
    // Selected marker
    private Marker selectedMarker;
    private Property selectedProperty;
    
    // List of map properties
    private List<Property> mapProperties;
    
    /**
     * Initialize the bean
     */
    @PostConstruct
    public void init() {
        mapModel = new DefaultMapModel();
        loadPropertiesForMap();
    }
    
    /**
     * Load properties with coordinates for the map
     */
    public void loadPropertiesForMap() {
        try {
            mapProperties = propertyService.getPropertiesWithCoordinates(
                    city, neighborhood, propertyType, operationType, minPrice, maxPrice, 1000);
            
            // Clear existing markers
            mapModel.getMarkers().clear();
            
            // Add markers for each property with coordinates
            for (Property property : mapProperties) {
                if (property.getLatitude() != null && property.getLongitude() != null) {
                    // Create marker position
                    LatLng position = new LatLng(property.getLatitude(), property.getLongitude());
                    
                    // Create marker with property information
                    Marker marker = new Marker(position, property.getTitle(), property, getMarkerIcon(property));
                    mapModel.addOverlay(marker);
                }
            }
            
            // Update map center if we have properties
            if (!mapProperties.isEmpty()) {
                updateMapCenter();
            }
        } catch (Exception e) {
            addErrorMessage("Error loading properties for map: " + e.getMessage());
            mapProperties = new ArrayList<>();
        }
    }
    
    /**
     * Determine marker icon based on property investment score
     */
    private String getMarkerIcon(Property property) {
        if (property.getInvestmentScore() != null) {
            if (property.getInvestmentScore() >= 70) {
                return "https://maps.google.com/mapfiles/ms/icons/green-dot.png";
            } else if (property.getInvestmentScore() >= 50) {
                return "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png";
            } else {
                return "https://maps.google.com/mapfiles/ms/icons/red-dot.png";
            }
        }
        return "https://maps.google.com/mapfiles/ms/icons/blue-dot.png";
    }
    
    /**
     * Update map center and zoom level based on property locations
     */
    private void updateMapCenter() {
        // Find bounds of all markers
        double minLat = Double.MAX_VALUE;
        double maxLat = Double.MIN_VALUE;
        double minLng = Double.MAX_VALUE;
        double maxLng = Double.MIN_VALUE;
        
        boolean hasValidCoordinates = false;
        
        for (Property property : mapProperties) {
            if (property.getLatitude() != null && property.getLongitude() != null) {
                minLat = Math.min(minLat, property.getLatitude());
                maxLat = Math.max(maxLat, property.getLatitude());
                minLng = Math.min(minLng, property.getLongitude());
                maxLng = Math.max(maxLng, property.getLongitude());
                hasValidCoordinates = true;
            }
        }
        
        if (hasValidCoordinates) {
            // Calculate center
            double centerLat = (minLat + maxLat) / 2;
            double centerLng = (minLng + maxLng) / 2;
            center = centerLat + ", " + centerLng;
            
            // Calculate appropriate zoom level
            zoom = GeoUtil.calculateZoomLevel(minLat, maxLat, minLng, maxLng);
        }
    }
    
    /**
     * Handle marker click event
     */
    public void onMarkerSelect(OverlaySelectEvent event) {
        selectedMarker = (Marker) event.getOverlay();
        
        // Get the property associated with this marker
        if (selectedMarker.getData() instanceof Property) {
            selectedProperty = (Property) selectedMarker.getData();
            
            // Load full property details if needed
            if (selectedProperty.getDescription() == null) {
                try {
                    selectedProperty = propertyService.getPropertyById(
                            selectedProperty.getId(), selectedProperty.getSource());
                } catch (Exception e) {
                    addErrorMessage("Error loading property details: " + e.getMessage());
                }
            }
        }
    }
    
    /**
     * Apply map filters and reload properties
     */
    public void applyFilters() {
        loadPropertiesForMap();
    }
    
    /**
     * Reset all map filters
     */
    public void resetFilters() {
        city = null;
        neighborhood = null;
        propertyType = null;
        operationType = "sale";
        minPrice = null;
        maxPrice = null;
        
        loadPropertiesForMap();
    }
    
    /**
     * Add an error message to be displayed in the UI
     */
    private void addErrorMessage(String message) {
        FacesContext.getCurrentInstance().addMessage(null, 
                new FacesMessage(FacesMessage.SEVERITY_ERROR, "Error", message));
    }
    
    // Getters and setters
    
    public MapModel getMapModel() {
        return mapModel;
    }
    
    public String getCenter() {
        return center;
    }
    
    public int getZoom() {
        return zoom;
    }
    
    public Marker getSelectedMarker() {
        return selectedMarker;
    }
    
    public Property getSelectedProperty() {
        return selectedProperty;
    }
    
    public void setSelectedProperty(Property selectedProperty) {
        this.selectedProperty = selectedProperty;
    }
    
    public String getCity() {
        return city;
    }
    
    public void setCity(String city) {
        this.city = city;
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
    
    public List<Property> getMapProperties() {
        return mapProperties;
    }
}
