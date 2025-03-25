package com.realestate.model;

import java.io.Serializable;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * Model class representing a real estate property
 */
public class Property implements Serializable {
    private static final long serialVersionUID = 1L;
    
    // Property identifiers
    private String id;
    private String url;
    private String source;
    
    // Basic property details
    private String title;
    private String description;
    private Double price;
    private List<Map<String, Object>> priceHistory;
    private String propertyType;
    private String operationType;
    
    // Physical characteristics
    private Double size;
    private Integer rooms;
    private Integer bathrooms;
    private Integer floor;
    private Boolean hasElevator;
    private String condition;
    private Integer yearBuilt;
    
    // Features and amenities
    private List<String> features;
    private String energyCert;
    
    // Location data
    private String address;
    private String neighborhood;
    private String district;
    private String city;
    private String province;
    private String postalCode;
    private Double latitude;
    private Double longitude;
    
    // Metadata
    private Date firstDetected;
    private Date lastUpdated;
    private Boolean isNew;
    private Integer daysListed;
    
    // Analysis data
    private Double pricePerSqm;
    private Double investmentScore;
    private List<Map<String, Object>> comparableProperties;

    // Default constructor
    public Property() {
    }
    
    // Constructor with essential fields
    public Property(String id, String source, String title, Double price) {
        this.id = id;
        this.source = source;
        this.title = title;
        this.price = price;
    }

    // Getters and setters
    
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public List<Map<String, Object>> getPriceHistory() {
        return priceHistory;
    }

    public void setPriceHistory(List<Map<String, Object>> priceHistory) {
        this.priceHistory = priceHistory;
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

    public Double getSize() {
        return size;
    }

    public void setSize(Double size) {
        this.size = size;
    }

    public Integer getRooms() {
        return rooms;
    }

    public void setRooms(Integer rooms) {
        this.rooms = rooms;
    }

    public Integer getBathrooms() {
        return bathrooms;
    }

    public void setBathrooms(Integer bathrooms) {
        this.bathrooms = bathrooms;
    }

    public Integer getFloor() {
        return floor;
    }

    public void setFloor(Integer floor) {
        this.floor = floor;
    }

    public Boolean getHasElevator() {
        return hasElevator;
    }

    public void setHasElevator(Boolean hasElevator) {
        this.hasElevator = hasElevator;
    }

    public String getCondition() {
        return condition;
    }

    public void setCondition(String condition) {
        this.condition = condition;
    }

    public Integer getYearBuilt() {
        return yearBuilt;
    }

    public void setYearBuilt(Integer yearBuilt) {
        this.yearBuilt = yearBuilt;
    }

    public List<String> getFeatures() {
        return features;
    }

    public void setFeatures(List<String> features) {
        this.features = features;
    }

    public String getEnergyCert() {
        return energyCert;
    }

    public void setEnergyCert(String energyCert) {
        this.energyCert = energyCert;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getNeighborhood() {
        return neighborhood;
    }

    public void setNeighborhood(String neighborhood) {
        this.neighborhood = neighborhood;
    }

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getPostalCode() {
        return postalCode;
    }

    public void setPostalCode(String postalCode) {
        this.postalCode = postalCode;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public Date getFirstDetected() {
        return firstDetected;
    }

    public void setFirstDetected(Date firstDetected) {
        this.firstDetected = firstDetected;
    }

    public Date getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(Date lastUpdated) {
        this.lastUpdated = lastUpdated;
    }

    public Boolean getIsNew() {
        return isNew;
    }

    public void setIsNew(Boolean isNew) {
        this.isNew = isNew;
    }

    public Integer getDaysListed() {
        return daysListed;
    }

    public void setDaysListed(Integer daysListed) {
        this.daysListed = daysListed;
    }

    public Double getPricePerSqm() {
        return pricePerSqm;
    }

    public void setPricePerSqm(Double pricePerSqm) {
        this.pricePerSqm = pricePerSqm;
    }

    public Double getInvestmentScore() {
        return investmentScore;
    }

    public void setInvestmentScore(Double investmentScore) {
        this.investmentScore = investmentScore;
    }

    public List<Map<String, Object>> getComparableProperties() {
        return comparableProperties;
    }

    public void setComparableProperties(List<Map<String, Object>> comparableProperties) {
        this.comparableProperties = comparableProperties;
    }
    
    /**
     * Get the property's location as a formatted string
     */
    public String getFormattedLocation() {
        StringBuilder sb = new StringBuilder();
        
        if (address != null && !address.isEmpty()) {
            sb.append(address);
        }
        
        if (neighborhood != null && !neighborhood.isEmpty()) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(neighborhood);
        }
        
        if (city != null && !city.isEmpty()) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(city);
        }
        
        if (province != null && !province.isEmpty() && !province.equals(city)) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(province);
        }
        
        if (postalCode != null && !postalCode.isEmpty()) {
            if (sb.length() > 0) sb.append(" (").append(postalCode).append(")");
            else sb.append(postalCode);
        }
        
        return sb.toString();
    }
    
    /**
     * Get a capitalized source name
     */
    public String getCapitalizedSource() {
        if (source == null || source.isEmpty()) {
            return "";
        }
        return source.substring(0, 1).toUpperCase() + source.substring(1);
    }
    
    /**
     * Get a user-friendly property type
     */
    public String getFormattedPropertyType() {
        if (propertyType == null || propertyType.isEmpty()) {
            return "Property";
        }
        
        return propertyType.substring(0, 1).toUpperCase() + propertyType.substring(1);
    }
    
    /**
     * Get CSS class for investment score
     */
    public String getInvestmentScoreClass() {
        if (investmentScore == null) {
            return "";
        }
        
        if (investmentScore >= 70) {
            return "score-high";
        } else if (investmentScore >= 50) {
            return "score-medium";
        } else {
            return "score-low";
        }
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Property other = (Property) obj;
        return id != null && id.equals(other.id) && source != null && source.equals(other.source);
    }
    
    @Override
    public int hashCode() {
        return 31 * (id != null ? id.hashCode() : 0) + (source != null ? source.hashCode() : 0);
    }
}
