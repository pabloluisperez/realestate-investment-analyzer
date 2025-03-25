"""
Service for retrieving and managing property data from MongoDB.
"""

import logging
from typing import List, Dict, Any, Optional
from bson.json_util import dumps, loads
import json
from datetime import datetime
from api.utils.db import get_db_connection

logger = logging.getLogger(__name__)


class PropertyService:
    """Service for retrieving and managing property data"""
    
    def __init__(self):
        """Initialize the property service"""
        self.db = get_db_connection()
        self.collection = self.db['properties']
    
    def get_properties(self, city=None, neighborhood=None, min_price=None, max_price=None,
                      property_type=None, operation_type=None, min_size=None, max_size=None, min_rooms=None,
                      limit=100, skip=0) -> List[Dict[str, Any]]:
        """
        Get properties with optional filtering
        
        Args:
            city: Filter by city
            neighborhood: Filter by neighborhood
            min_price: Minimum price
            max_price: Maximum price
            property_type: Type of property (apartment, house, etc.)
            operation_type: Type of operation (sale, rent)
            min_size: Minimum size in square meters
            max_size: Maximum size in square meters
            min_rooms: Minimum number of rooms
            limit: Maximum number of properties to return
            skip: Number of properties to skip (for pagination)
            
        Returns:
            List of property dictionaries
        """
        try:
            # Build query filter
            query_filter = {}
            
            if city:
                query_filter['city'] = city
            
            if neighborhood:
                query_filter['neighborhood'] = neighborhood
            
            if property_type:
                query_filter['property_type'] = property_type
            
            if operation_type:
                query_filter['operation_type'] = operation_type
            
            price_filter = {}
            if min_price is not None:
                price_filter['$gte'] = min_price
            if max_price is not None:
                price_filter['$lte'] = max_price
            if price_filter:
                query_filter['price'] = price_filter
            
            size_filter = {}
            if min_size is not None:
                size_filter['$gte'] = min_size
            if max_size is not None:
                size_filter['$lte'] = max_size
            if size_filter:
                query_filter['size'] = size_filter
            
            if min_rooms is not None:
                query_filter['rooms'] = {'$gte': min_rooms}
            
            # Query database
            try:
                cursor = self.collection.find(query_filter).limit(limit).skip(skip)
                # Convert to list of dictionaries
                properties = loads(dumps(list(cursor)))
                # Convert MongoDB dates to string
                properties = self._format_properties(properties)
            except Exception as e:
                logger.warning(f"Error querying database: {str(e)}, returning empty list")
                properties = []
            
            return properties
        except Exception as e:
            logger.error(f"Error getting properties: {str(e)}")
            return []
    
    def get_property_by_id(self, property_id: str, source: str) -> Optional[Dict[str, Any]]:
        """
        Get a property by its ID and source
        
        Args:
            property_id: The property ID
            source: The source website (e.g., 'idealista', 'fotocasa')
            
        Returns:
            Property dictionary or None if not found
        """
        try:
            # Query database
            property_data = self.collection.find_one({'id': property_id, 'source': source})
            
            if property_data:
                # Convert MongoDB document to dictionary
                property_dict = loads(dumps(property_data))
                
                # Convert MongoDB dates to string
                property_dict = self._format_property(property_dict)
                
                return property_dict
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting property by ID: {str(e)}")
            return None
    
    def get_properties_with_coordinates(self, city=None, neighborhood=None, min_price=None,
                                       max_price=None, property_type=None, operation_type=None,
                                       limit=1000) -> List[Dict[str, Any]]:
        """
        Get properties with coordinates for map display
        
        Args:
            city: Filter by city
            neighborhood: Filter by neighborhood
            min_price: Minimum price
            max_price: Maximum price
            property_type: Type of property (apartment, house, etc.)
            operation_type: Type of operation (sale, rent)
            limit: Maximum number of properties to return
            
        Returns:
            List of property dictionaries with coordinates
        """
        try:
            # Build query filter
            query_filter = {
                'latitude': {'$exists': True, '$ne': None},
                'longitude': {'$exists': True, '$ne': None}
            }
            
            if city:
                query_filter['city'] = city
            
            if neighborhood:
                query_filter['neighborhood'] = neighborhood
            
            if property_type:
                query_filter['property_type'] = property_type
            
            if operation_type:
                query_filter['operation_type'] = operation_type
            
            price_filter = {}
            if min_price is not None:
                price_filter['$gte'] = min_price
            if max_price is not None:
                price_filter['$lte'] = max_price
            if price_filter:
                query_filter['price'] = price_filter
            
            # Query database
            try:
                cursor = self.collection.find(
                    query_filter,
                    {
                        'id': 1, 'source': 1, 'title': 1, 'price': 1, 'size': 1,
                        'latitude': 1, 'longitude': 1, 'property_type': 1,
                        'investment_score': 1, 'url': 1, 'city': 1, 'neighborhood': 1
                    }
                ).limit(limit)
                
                # Convert to list of dictionaries
                properties = loads(dumps(list(cursor)))
            except Exception as e:
                logger.warning(f"Error querying database: {str(e)}, returning empty list")
                properties = []
            
            return properties
        except Exception as e:
            logger.error(f"Error getting properties with coordinates: {str(e)}")
            return []
    
    def get_cities(self) -> List[str]:
        """
        Get a list of all cities in the database
        
        Returns:
            List of city names
        """
        try:
            # Query distinct cities
            cities = self.collection.distinct('city')
            
            # Filter out None values and sort
            cities = [city for city in cities if city]
            cities.sort()
            
            return cities
        except Exception as e:
            logger.error(f"Error getting cities: {str(e)}")
            return []
    
    def get_neighborhoods(self, city: str) -> List[str]:
        """
        Get neighborhoods for a specific city
        
        Args:
            city: The city name
            
        Returns:
            List of neighborhood names
        """
        try:
            # Query distinct neighborhoods for the city
            neighborhoods = self.collection.distinct('neighborhood', {'city': city})
            
            # Filter out None values and sort
            neighborhoods = [n for n in neighborhoods if n]
            neighborhoods.sort()
            
            return neighborhoods
        except Exception as e:
            logger.error(f"Error getting neighborhoods: {str(e)}")
            return []
    
    def _format_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format a list of property dictionaries
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            Formatted list of property dictionaries
        """
        return [self._format_property(prop) for prop in properties]
    
    def _format_property(self, property_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a property dictionary for output
        
        Args:
            property_dict: Property dictionary
            
        Returns:
            Formatted property dictionary
        """
        # Convert MongoDB ObjectId to string
        if '_id' in property_dict:
            property_dict['_id'] = str(property_dict['_id'])
        
        # Convert date fields to strings
        date_fields = ['first_detected', 'last_updated']
        for field in date_fields:
            if field in property_dict and property_dict[field]:
                # Handle both datetime objects and string dates
                if isinstance(property_dict[field], dict) and '$date' in property_dict[field]:
                    # Handle MongoDB date format
                    property_dict[field] = property_dict[field]['$date']
                    
                    # If it's a timestamp, convert to ISO format
                    if isinstance(property_dict[field], int):
                        property_dict[field] = datetime.fromtimestamp(
                            property_dict[field] / 1000
                        ).isoformat()
        
        # Format price history dates
        if 'price_history' in property_dict and property_dict['price_history']:
            for entry in property_dict['price_history']:
                if 'date' in entry and entry['date']:
                    if isinstance(entry['date'], dict) and '$date' in entry['date']:
                        entry['date'] = entry['date']['$date']
                        
                        # If it's a timestamp, convert to ISO format
                        if isinstance(entry['date'], int):
                            entry['date'] = datetime.fromtimestamp(
                                entry['date'] / 1000
                            ).isoformat()
        
        return property_dict
