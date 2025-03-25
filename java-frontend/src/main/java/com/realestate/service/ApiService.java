package com.realestate.service;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.enterprise.context.ApplicationScoped;
import javax.inject.Named;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonValue;
import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.realestate.model.Property;
import com.realestate.model.InvestmentOpportunity;

/**
 * Service for communicating with the backend API
 */
@Named
@ApplicationScoped
public class ApiService implements Serializable {
    private static final long serialVersionUID = 1L;
    
    // API base URL
    private static final String API_BASE_URL = "http://localhost:8000/api";
    
    /**
     * Get a list of all cities
     */
    public List<String> getCities() throws Exception {
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("cities");
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get cities: " + response.getStatus());
        }
        
        JsonArray jsonArray = response.readEntity(JsonArray.class);
        List<String> cities = new ArrayList<>();
        
        for (JsonValue value : jsonArray) {
            cities.add(value.toString().replaceAll("\"", ""));
        }
        
        return cities;
    }
    
    /**
     * Get neighborhoods for a specific city
     */
    public List<String> getNeighborhoods(String city) throws Exception {
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("neighborhoods")
                .queryParam("city", city);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get neighborhoods: " + response.getStatus());
        }
        
        JsonArray jsonArray = response.readEntity(JsonArray.class);
        List<String> neighborhoods = new ArrayList<>();
        
        for (JsonValue value : jsonArray) {
            neighborhoods.add(value.toString().replaceAll("\"", ""));
        }
        
        return neighborhoods;
    }
    
    /**
     * Get properties with optional filtering
     */
    public List<Property> getProperties(String city, String neighborhood, String propertyType,
            String operationType, Double minPrice, Double maxPrice, Double minSize, Double maxSize,
            Integer minRooms, int limit, int skip) throws Exception {
        
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("properties");
        
        // Add query parameters if they are not null
        if (city != null && !city.isEmpty()) {
            target = target.queryParam("city", city);
        }
        
        if (neighborhood != null && !neighborhood.isEmpty()) {
            target = target.queryParam("neighborhood", neighborhood);
        }
        
        if (propertyType != null && !propertyType.isEmpty()) {
            target = target.queryParam("property_type", propertyType);
        }
        
        if (operationType != null && !operationType.isEmpty()) {
            target = target.queryParam("operation_type", operationType);
        }
        
        if (minPrice != null) {
            target = target.queryParam("min_price", minPrice);
        }
        
        if (maxPrice != null) {
            target = target.queryParam("max_price", maxPrice);
        }
        
        if (minSize != null) {
            target = target.queryParam("min_size", minSize);
        }
        
        if (maxSize != null) {
            target = target.queryParam("max_size", maxSize);
        }
        
        if (minRooms != null) {
            target = target.queryParam("min_rooms", minRooms);
        }
        
        target = target.queryParam("limit", limit);
        target = target.queryParam("skip", skip);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get properties: " + response.getStatus());
        }
        
        JsonArray jsonArray = response.readEntity(JsonArray.class);
        List<Property> properties = new ArrayList<>();
        
        for (JsonValue value : jsonArray) {
            properties.add(jsonToProperty((JsonObject) value));
        }
        
        return properties;
    }
    
    /**
     * Get properties with coordinates for map display
     */
    public List<Property> getPropertiesWithCoordinates(String city, String neighborhood,
            String propertyType, String operationType, Double minPrice, Double maxPrice,
            int limit) throws Exception {
        
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("properties/map");
        
        // Add query parameters if they are not null
        if (city != null && !city.isEmpty()) {
            target = target.queryParam("city", city);
        }
        
        if (neighborhood != null && !neighborhood.isEmpty()) {
            target = target.queryParam("neighborhood", neighborhood);
        }
        
        if (propertyType != null && !propertyType.isEmpty()) {
            target = target.queryParam("property_type", propertyType);
        }
        
        if (operationType != null && !operationType.isEmpty()) {
            target = target.queryParam("operation_type", operationType);
        }
        
        if (minPrice != null) {
            target = target.queryParam("min_price", minPrice);
        }
        
        if (maxPrice != null) {
            target = target.queryParam("max_price", maxPrice);
        }
        
        target = target.queryParam("limit", limit);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get map properties: " + response.getStatus());
        }
        
        JsonArray jsonArray = response.readEntity(JsonArray.class);
        List<Property> properties = new ArrayList<>();
        
        for (JsonValue value : jsonArray) {
            properties.add(jsonToProperty((JsonObject) value));
        }
        
        return properties;
    }
    
    /**
     * Get a specific property by ID and source
     */
    public Property getPropertyById(String propertyId, String source) throws Exception {
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("properties/" + propertyId)
                .queryParam("source", source);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get property: " + response.getStatus());
        }
        
        JsonObject jsonObject = response.readEntity(JsonObject.class);
        return jsonToProperty(jsonObject);
    }
    
    /**
     * Get investment opportunities based on filters
     */
    public List<InvestmentOpportunity> getInvestmentOpportunities(String city, String neighborhood,
            String propertyType, String operationType, Integer minScore, int limit, int skip) throws Exception {
        
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("investment/opportunities");
        
        // Add query parameters if they are not null
        if (city != null && !city.isEmpty()) {
            target = target.queryParam("city", city);
        }
        
        if (neighborhood != null && !neighborhood.isEmpty()) {
            target = target.queryParam("neighborhood", neighborhood);
        }
        
        if (propertyType != null && !propertyType.isEmpty()) {
            target = target.queryParam("property_type", propertyType);
        }
        
        if (operationType != null && !operationType.isEmpty()) {
            target = target.queryParam("operation_type", operationType);
        }
        
        if (minScore != null) {
            target = target.queryParam("min_score", minScore);
        }
        
        target = target.queryParam("limit", limit);
        target = target.queryParam("skip", skip);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get investment opportunities: " + response.getStatus());
        }
        
        JsonArray jsonArray = response.readEntity(JsonArray.class);
        List<InvestmentOpportunity> opportunities = new ArrayList<>();
        
        for (JsonValue value : jsonArray) {
            opportunities.add(jsonToOpportunity((JsonObject) value));
        }
        
        return opportunities;
    }
    
    /**
     * Get detailed investment analysis for a specific property
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getPropertyAnalysis(String propertyId, String source) throws Exception {
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target(API_BASE_URL).path("investment/analysis/" + propertyId)
                .queryParam("source", source);
        
        Response response = target.request(MediaType.APPLICATION_JSON).get();
        
        if (response.getStatus() != 200) {
            throw new Exception("Failed to get property analysis: " + response.getStatus());
        }
        
        JsonObject jsonObject = response.readEntity(JsonObject.class);
        
        // Convert JsonObject to Map
        Map<String, Object> analysis = new HashMap<>();
        
        // Property data
        if (jsonObject.containsKey("property")) {
            analysis.put("property", jsonToProperty(jsonObject.getJsonObject("property")));
        }
        
        // Area data
        if (jsonObject.containsKey("area_data")) {
            Map<String, Object> areaData = new HashMap<>();
            JsonObject areaJson = jsonObject.getJsonObject("area_data");
            
            if (areaJson.containsKey("city")) {
                areaData.put("city", areaJson.getString("city"));
            }
            
            if (areaJson.containsKey("neighborhood")) {
                areaData.put("neighborhood", areaJson.getString("neighborhood", null));
            }
            
            if (areaJson.containsKey("property_count")) {
                areaData.put("propertyCount", areaJson.getInt("property_count"));
            }
            
            // Parse price_per_sqm data
            if (areaJson.containsKey("price_per_sqm") && !areaJson.isNull("price_per_sqm")) {
                Map<String, Object> priceData = new HashMap<>();
                JsonObject priceJson = areaJson.getJsonObject("price_per_sqm");
                
                if (priceJson.containsKey("avg_price_per_sqm")) {
                    priceData.put("avgPricePerSqm", priceJson.getJsonNumber("avg_price_per_sqm").doubleValue());
                }
                
                if (priceJson.containsKey("min_price_per_sqm")) {
                    priceData.put("minPricePerSqm", priceJson.getJsonNumber("min_price_per_sqm").doubleValue());
                }
                
                if (priceJson.containsKey("max_price_per_sqm")) {
                    priceData.put("maxPricePerSqm", priceJson.getJsonNumber("max_price_per_sqm").doubleValue());
                }
                
                if (priceJson.containsKey("count")) {
                    priceData.put("count", priceJson.getInt("count"));
                }
                
                areaData.put("pricePerSqm", priceData);
            }
            
            // Parse time_on_market data
            if (areaJson.containsKey("time_on_market") && !areaJson.isNull("time_on_market")) {
                Map<String, Object> timeData = new HashMap<>();
                JsonObject timeJson = areaJson.getJsonObject("time_on_market");
                
                if (timeJson.containsKey("avg_days_listed")) {
                    timeData.put("avgDaysListed", timeJson.getJsonNumber("avg_days_listed").doubleValue());
                }
                
                if (timeJson.containsKey("count")) {
                    timeData.put("count", timeJson.getInt("count"));
                }
                
                areaData.put("timeOnMarket", timeData);
            }
            
            // Parse property_types data
            if (areaJson.containsKey("property_types")) {
                List<Map<String, Object>> propertyTypes = new ArrayList<>();
                JsonArray typesArray = areaJson.getJsonArray("property_types");
                
                for (JsonValue value : typesArray) {
                    JsonObject typeJson = (JsonObject) value;
                    Map<String, Object> typeData = new HashMap<>();
                    
                    if (typeJson.containsKey("_id")) {
                        typeData.put("type", typeJson.getString("_id"));
                    }
                    
                    if (typeJson.containsKey("count")) {
                        typeData.put("count", typeJson.getInt("count"));
                    }
                    
                    propertyTypes.add(typeData);
                }
                
                areaData.put("propertyTypes", propertyTypes);
            }
            
            analysis.put("areaData", areaData);
        }
        
        // Price insights
        if (jsonObject.containsKey("price_insights")) {
            Map<String, Object> priceInsights = new HashMap<>();
            JsonObject insightsJson = jsonObject.getJsonObject("price_insights");
            
            if (insightsJson.containsKey("price_difference")) {
                priceInsights.put("priceDifference", insightsJson.getJsonNumber("price_difference").doubleValue());
            }
            
            if (insightsJson.containsKey("price_difference_label")) {
                priceInsights.put("priceDifferenceLabel", insightsJson.getString("price_difference_label"));
            }
            
            if (insightsJson.containsKey("price_percentile")) {
                priceInsights.put("pricePercentile", insightsJson.getJsonNumber("price_percentile").doubleValue());
            }
            
            if (insightsJson.containsKey("price_change")) {
                priceInsights.put("priceChange", insightsJson.getJsonNumber("price_change").doubleValue());
            }
            
            if (insightsJson.containsKey("price_changes_count")) {
                priceInsights.put("priceChangesCount", insightsJson.getInt("price_changes_count"));
            }
            
            analysis.put("priceInsights", priceInsights);
        }
        
        // Investment metrics
        if (jsonObject.containsKey("investment_metrics")) {
            Map<String, Object> investmentMetrics = new HashMap<>();
            JsonObject metricsJson = jsonObject.getJsonObject("investment_metrics");
            
            if (metricsJson.containsKey("investment_score")) {
                investmentMetrics.put("investmentScore", metricsJson.getJsonNumber("investment_score").doubleValue());
            }
            
            if (metricsJson.containsKey("renovation_roi")) {
                investmentMetrics.put("renovationRoi", metricsJson.getJsonNumber("renovation_roi").doubleValue());
            }
            
            if (metricsJson.containsKey("renovation_cost")) {
                investmentMetrics.put("renovationCost", metricsJson.getJsonNumber("renovation_cost").doubleValue());
            }
            
            if (metricsJson.containsKey("estimated_market_value")) {
                investmentMetrics.put("estimatedMarketValue", metricsJson.getJsonNumber("estimated_market_value").doubleValue());
            }
            
            if (metricsJson.containsKey("price_to_value_ratio")) {
                investmentMetrics.put("priceToValueRatio", metricsJson.getJsonNumber("price_to_value_ratio").doubleValue());
            }
            
            if (metricsJson.containsKey("potential_appreciation")) {
                investmentMetrics.put("potentialAppreciation", metricsJson.getJsonNumber("potential_appreciation").doubleValue());
            }
            
            if (metricsJson.containsKey("estimated_monthly_rent")) {
                investmentMetrics.put("estimatedMonthlyRent", metricsJson.getJsonNumber("estimated_monthly_rent").doubleValue());
            }
            
            if (metricsJson.containsKey("estimated_rental_yield")) {
                investmentMetrics.put("estimatedRentalYield", metricsJson.getJsonNumber("estimated_rental_yield").doubleValue());
            }
            
            if (metricsJson.containsKey("liquidity_score")) {
                investmentMetrics.put("liquidityScore", metricsJson.getJsonNumber("liquidity_score").doubleValue());
            }
            
            if (metricsJson.containsKey("avg_days_on_market")) {
                investmentMetrics.put("avgDaysOnMarket", metricsJson.getJsonNumber("avg_days_on_market").doubleValue());
            }
            
            analysis.put("investmentMetrics", investmentMetrics);
        }
        
        // Similar properties
        if (jsonObject.containsKey("similar_properties")) {
            List<Property> similarProperties = new ArrayList<>();
            JsonArray propsArray = jsonObject.getJsonArray("similar_properties");
            
            for (JsonValue value : propsArray) {
                JsonObject propJson = (JsonObject) value;
                similarProperties.add(jsonToProperty(propJson));
            }
            
            analysis.put("similarProperties", similarProperties);
        }
        
        return analysis;
    }
    
    /**
     * Convert a JSON object to a Property object
     */
    private Property jsonToProperty(JsonObject json) {
        Property property = new Property();
        
        // Property identifiers
        if (json.containsKey("id")) {
            property.setId(json.getString("id"));
        }
        
        if (json.containsKey("url")) {
            property.setUrl(json.getString("url", null));
        }
        
        if (json.containsKey("source")) {
            property.setSource(json.getString("source"));
        }
        
        // Basic property details
        if (json.containsKey("title")) {
            property.setTitle(json.getString("title", null));
        }
        
        if (json.containsKey("description")) {
            property.setDescription(json.getString("description", null));
        }
        
        if (json.containsKey("price") && !json.isNull("price")) {
            property.setPrice(json.getJsonNumber("price").doubleValue());
        }
        
        if (json.containsKey("property_type")) {
            property.setPropertyType(json.getString("property_type", null));
        }
        
        if (json.containsKey("operation_type")) {
            property.setOperationType(json.getString("operation_type", null));
        }
        
        // Physical characteristics
        if (json.containsKey("size") && !json.isNull("size")) {
            property.setSize(json.getJsonNumber("size").doubleValue());
        }
        
        if (json.containsKey("rooms") && !json.isNull("rooms")) {
            property.setRooms(json.getInt("rooms"));
        }
        
        if (json.containsKey("bathrooms") && !json.isNull("bathrooms")) {
            property.setBathrooms(json.getInt("bathrooms"));
        }
        
        if (json.containsKey("floor") && !json.isNull("floor")) {
            property.setFloor(json.getInt("floor"));
        }
        
        if (json.containsKey("has_elevator")) {
            property.setHasElevator(json.getBoolean("has_elevator", false));
        }
        
        if (json.containsKey("condition")) {
            property.setCondition(json.getString("condition", null));
        }
        
        if (json.containsKey("year_built") && !json.isNull("year_built")) {
            property.setYearBuilt(json.getInt("year_built"));
        }
        
        // Location data
        if (json.containsKey("address")) {
            property.setAddress(json.getString("address", null));
        }
        
        if (json.containsKey("neighborhood")) {
            property.setNeighborhood(json.getString("neighborhood", null));
        }
        
        if (json.containsKey("district")) {
            property.setDistrict(json.getString("district", null));
        }
        
        if (json.containsKey("city")) {
            property.setCity(json.getString("city", null));
        }
        
        if (json.containsKey("province")) {
            property.setProvince(json.getString("province", null));
        }
        
        if (json.containsKey("postal_code")) {
            property.setPostalCode(json.getString("postal_code", null));
        }
        
        if (json.containsKey("latitude") && !json.isNull("latitude")) {
            property.setLatitude(json.getJsonNumber("latitude").doubleValue());
        }
        
        if (json.containsKey("longitude") && !json.isNull("longitude")) {
            property.setLongitude(json.getJsonNumber("longitude").doubleValue());
        }
        
        // Metadata
        if (json.containsKey("first_detected")) {
            property.setFirstDetected(new Date()); // Parse date from string if needed
        }
        
        if (json.containsKey("last_updated")) {
            property.setLastUpdated(new Date()); // Parse date from string if needed
        }
        
        if (json.containsKey("is_new")) {
            property.setIsNew(json.getBoolean("is_new", true));
        }
        
        if (json.containsKey("days_listed") && !json.isNull("days_listed")) {
            property.setDaysListed(json.getInt("days_listed"));
        }
        
        // Analysis data
        if (json.containsKey("price_per_sqm") && !json.isNull("price_per_sqm")) {
            property.setPricePerSqm(json.getJsonNumber("price_per_sqm").doubleValue());
        }
        
        if (json.containsKey("investment_score") && !json.isNull("investment_score")) {
            property.setInvestmentScore(json.getJsonNumber("investment_score").doubleValue());
        }
        
        return property;
    }
    
    /**
     * Convert a JSON object to an InvestmentOpportunity object
     */
    private InvestmentOpportunity jsonToOpportunity(JsonObject json) {
        InvestmentOpportunity opportunity = new InvestmentOpportunity();
        
        // Basic details
        if (json.containsKey("property_id")) {
            opportunity.setPropertyId(json.getString("property_id"));
        }
        
        if (json.containsKey("source")) {
            opportunity.setSource(json.getString("source"));
        }
        
        if (json.containsKey("title")) {
            opportunity.setTitle(json.getString("title", null));
        }
        
        if (json.containsKey("price") && !json.isNull("price")) {
            opportunity.setPrice(json.getJsonNumber("price").doubleValue());
        }
        
        if (json.containsKey("size") && !json.isNull("size")) {
            opportunity.setSize(json.getJsonNumber("size").doubleValue());
        }
        
        // Location data
        if (json.containsKey("city")) {
            opportunity.setCity(json.getString("city", null));
        }
        
        if (json.containsKey("neighborhood")) {
            opportunity.setNeighborhood(json.getString("neighborhood", null));
        }
        
        // Property details
        if (json.containsKey("property_type")) {
            opportunity.setPropertyType(json.getString("property_type", null));
        }
        
        if (json.containsKey("operation_type")) {
            opportunity.setOperationType(json.getString("operation_type", null));
        }
        
        // Investment metrics
        if (json.containsKey("investment_score") && !json.isNull("investment_score")) {
            opportunity.setInvestmentScore(json.getJsonNumber("investment_score").doubleValue());
        }
        
        if (json.containsKey("price_per_sqm") && !json.isNull("price_per_sqm")) {
            opportunity.setPricePerSqm(json.getJsonNumber("price_per_sqm").doubleValue());
        }
        
        if (json.containsKey("avg_area_price_per_sqm") && !json.isNull("avg_area_price_per_sqm")) {
            opportunity.setAvgAreaPricePerSqm(json.getJsonNumber("avg_area_price_per_sqm").doubleValue());
        }
        
        if (json.containsKey("price_difference") && !json.isNull("price_difference")) {
            opportunity.setPriceDifference(json.getJsonNumber("price_difference").doubleValue());
        }
        
        if (json.containsKey("estimated_roi") && !json.isNull("estimated_roi")) {
            opportunity.setEstimatedRoi(json.getJsonNumber("estimated_roi").doubleValue());
        }
        
        if (json.containsKey("comparable_count") && !json.isNull("comparable_count")) {
            opportunity.setComparableCount(json.getInt("comparable_count"));
        }
        
        // Location coordinates
        if (json.containsKey("latitude") && !json.isNull("latitude")) {
            opportunity.setLatitude(json.getJsonNumber("latitude").doubleValue());
        }
        
        if (json.containsKey("longitude") && !json.isNull("longitude")) {
            opportunity.setLongitude(json.getJsonNumber("longitude").doubleValue());
        }
        
        // URL
        if (json.containsKey("url")) {
            opportunity.setUrl(json.getString("url", null));
        }
        
        return opportunity;
    }
}
