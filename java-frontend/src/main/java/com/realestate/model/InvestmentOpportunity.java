package com.realestate.model;

import java.io.Serializable;

/**
 * Model class representing a real estate investment opportunity
 */
public class InvestmentOpportunity implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String propertyId;
    private String source;
    private String title;
    private Double price;
    private Double size;
    private String city;
    private String neighborhood;
    private String propertyType;
    private String operationType;
    private Double investmentScore;
    private Double pricePerSqm;
    private Double avgAreaPricePerSqm;
    private Double priceDifference;  // Percentage difference from average
    private Double estimatedRoi;     // Estimated Return on Investment
    private Integer comparableCount;
    private Double latitude;
    private Double longitude;
    private String url;

    // Default constructor
    public InvestmentOpportunity() {
    }
    
    // Constructor with essential fields
    public InvestmentOpportunity(String propertyId, String source, String title, Double price, Double investmentScore) {
        this.propertyId = propertyId;
        this.source = source;
        this.title = title;
        this.price = price;
        this.investmentScore = investmentScore;
    }

    // Getters and setters
    
    public String getPropertyId() {
        return propertyId;
    }

    public void setPropertyId(String propertyId) {
        this.propertyId = propertyId;
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

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public Double getSize() {
        return size;
    }

    public void setSize(Double size) {
        this.size = size;
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

    public Double getInvestmentScore() {
        return investmentScore;
    }

    public void setInvestmentScore(Double investmentScore) {
        this.investmentScore = investmentScore;
    }

    public Double getPricePerSqm() {
        return pricePerSqm;
    }

    public void setPricePerSqm(Double pricePerSqm) {
        this.pricePerSqm = pricePerSqm;
    }

    public Double getAvgAreaPricePerSqm() {
        return avgAreaPricePerSqm;
    }

    public void setAvgAreaPricePerSqm(Double avgAreaPricePerSqm) {
        this.avgAreaPricePerSqm = avgAreaPricePerSqm;
    }

    public Double getPriceDifference() {
        return priceDifference;
    }

    public void setPriceDifference(Double priceDifference) {
        this.priceDifference = priceDifference;
    }

    public Double getEstimatedRoi() {
        return estimatedRoi;
    }

    public void setEstimatedRoi(Double estimatedRoi) {
        this.estimatedRoi = estimatedRoi;
    }

    public Integer getComparableCount() {
        return comparableCount;
    }

    public void setComparableCount(Integer comparableCount) {
        this.comparableCount = comparableCount;
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

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
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
     * Get the location as a formatted string
     */
    public String getFormattedLocation() {
        StringBuilder sb = new StringBuilder();
        
        if (city != null && !city.isEmpty()) {
            sb.append(city);
        }
        
        if (neighborhood != null && !neighborhood.isEmpty()) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(neighborhood);
        }
        
        return sb.toString();
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
    
    /**
     * Get CSS class for price difference
     */
    public String getPriceDifferenceClass() {
        if (priceDifference == null) {
            return "";
        }
        
        if (priceDifference > 0) {
            return "text-success";
        } else {
            return "text-danger";
        }
    }
    
    /**
     * Get formatted price difference text
     */
    public String getFormattedPriceDifference() {
        if (priceDifference == null) {
            return "";
        }
        
        if (priceDifference > 0) {
            return String.format("%.1f%% below average", priceDifference);
        } else {
            return String.format("%.1f%% above average", Math.abs(priceDifference));
        }
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        InvestmentOpportunity other = (InvestmentOpportunity) obj;
        return propertyId != null && propertyId.equals(other.propertyId) && 
               source != null && source.equals(other.source);
    }
    
    @Override
    public int hashCode() {
        return 31 * (propertyId != null ? propertyId.hashCode() : 0) + 
                (source != null ? source.hashCode() : 0);
    }
}
