"""
Define the data structure for scraped items
"""

import scrapy
from datetime import datetime


class PropertyItem(scrapy.Item):
    """
    Item representing a real estate property listing
    """
    # Property identifiers
    id = scrapy.Field()  # Unique ID from the source website
    url = scrapy.Field()  # URL of the property listing
    source = scrapy.Field()  # Source website (e.g., "idealista", "fotocasa")
    
    # Basic property details
    title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()  # Current price in EUR
    price_history = scrapy.Field()  # List of historical prices with dates
    property_type = scrapy.Field()  # Type: apartment, house, etc.
    operation_type = scrapy.Field()  # Sale, rent, etc.
    
    # Physical characteristics
    size = scrapy.Field()  # Size in square meters
    rooms = scrapy.Field()  # Number of rooms
    bathrooms = scrapy.Field()  # Number of bathrooms
    floor = scrapy.Field()  # Floor number
    has_elevator = scrapy.Field()  # Boolean
    condition = scrapy.Field()  # New, good condition, to be renovated, etc.
    year_built = scrapy.Field()
    
    # Features and amenities
    features = scrapy.Field()  # List of features (parking, swimming pool, etc.)
    energy_cert = scrapy.Field()  # Energy certification
    
    # Location data
    address = scrapy.Field()
    neighborhood = scrapy.Field()
    district = scrapy.Field()
    city = scrapy.Field()
    province = scrapy.Field()
    postal_code = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    
    # Metadata
    first_detected = scrapy.Field()  # When we first scraped this property
    last_updated = scrapy.Field()  # Last time the property was updated
    is_new = scrapy.Field()  # Boolean indicating if this is a new listing
    days_listed = scrapy.Field()  # Number of days listed
    
    # Analysis data
    price_per_sqm = scrapy.Field()  # Price per square meter
    investment_score = scrapy.Field()  # Score from 0-100 indicating investment potential
    comparable_properties = scrapy.Field()  # List of similar property IDs
    
    # Internal fields for processing
    raw_data = scrapy.Field()  # Raw data for debugging

    def __init__(self, *args, **kwargs):
        super(PropertyItem, self).__init__(*args, **kwargs)
        self.setdefault('first_detected', datetime.now())
        self.setdefault('last_updated', datetime.now())
        self.setdefault('is_new', True)
