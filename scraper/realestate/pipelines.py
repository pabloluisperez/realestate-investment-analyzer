"""
Item pipelines for processing and storing scraped properties
"""

import logging
import pymongo
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class DuplicateDetectionPipeline:
    """
    Pipeline for detecting and handling duplicate items.
    Determines if a property listing is new or has been modified.
    """
    
    def __init__(self):
        self.mongodb_uri = None
        self.mongodb_db = None
        self.mongodb_collection = None
        self.client = None
        self.db = None
        self.collection = None
        
    def open_spider(self, spider):
        self.mongodb_uri = spider.settings.get('MONGODB_URI')
        self.mongodb_db = spider.settings.get('MONGODB_DATABASE')
        self.mongodb_collection = spider.settings.get('MONGODB_COLLECTION')
        
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.collection = self.db[self.mongodb_collection]
        logger.info(f"Connected to MongoDB: {self.mongodb_uri}, DB: {self.mongodb_db}")
    
    def close_spider(self, spider):
        self.client.close()
        
    def process_item(self, item, spider):
        # Check if this property already exists in the database
        existing_property = self.collection.find_one({
            'id': item['id'],
            'source': item['source']
        })
        
        if existing_property:
            # It's not a new property, check if it has been modified
            item['is_new'] = False
            item['first_detected'] = existing_property.get('first_detected', datetime.now())
            
            # Check if price has changed
            if item.get('price') != existing_property.get('price'):
                # Price has changed, update price history
                price_history = existing_property.get('price_history', [])
                price_history.append({
                    'price': existing_property.get('price'),
                    'date': existing_property.get('last_updated', datetime.now())
                })
                item['price_history'] = price_history
                logger.info(f"Price change detected for property {item['id']} from {existing_property.get('price')} to {item['price']}")
            else:
                # No price change, keep existing price history
                item['price_history'] = existing_property.get('price_history', [])
                
            # Calculate days listed
            days_listed = (datetime.now() - item['first_detected']).days
            item['days_listed'] = days_listed
        else:
            # It's a new property
            item['is_new'] = True
            item['days_listed'] = 0
            item['price_history'] = []
            logger.info(f"New property detected: {item['id']} from {item['source']}")
        
        # Update the last_updated timestamp
        item['last_updated'] = datetime.now()
        
        # Calculate price per sqm if both price and size are available
        if 'price' in item and 'size' in item and item['size'] > 0:
            item['price_per_sqm'] = item['price'] / item['size']
        
        return item


class MongoPipeline:
    """
    Pipeline for storing items in MongoDB and performing investment analysis
    """
    
    def __init__(self):
        self.mongodb_uri = None
        self.mongodb_db = None
        self.mongodb_collection = None
        self.client = None
        self.db = None
        self.collection = None
        self.ml_model = None
        self.scaler = None
        
    def open_spider(self, spider):
        self.mongodb_uri = spider.settings.get('MONGODB_URI')
        self.mongodb_db = spider.settings.get('MONGODB_DATABASE')
        self.mongodb_collection = spider.settings.get('MONGODB_COLLECTION')
        
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.collection = self.db[self.mongodb_collection]
        
        # Create indexes
        self.collection.create_index([("id", pymongo.ASCENDING), ("source", pymongo.ASCENDING)], unique=True)
        self.collection.create_index([("latitude", pymongo.ASCENDING), ("longitude", pymongo.ASCENDING)])
        self.collection.create_index([("city", pymongo.ASCENDING), ("neighborhood", pymongo.ASCENDING)])
        
        # Initialize the ML model
        self._initialize_ml_model()
        
        logger.info(f"MongoDB pipeline initialized with URI: {self.mongodb_uri}")
    
    def close_spider(self, spider):
        self.client.close()
        
    def process_item(self, item, spider):
        try:
            # Run investment analysis on the item
            self._analyze_investment_potential(item)
            
            # Convert item to dict
            property_dict = dict(item)
            
            # Use upsert to update if exists, insert if not
            self.collection.update_one(
                {'id': item['id'], 'source': item['source']},
                {'$set': property_dict},
                upsert=True
            )
            logger.debug(f"Saved property to MongoDB: {item['id']}")
            return item
        except DuplicateKeyError:
            logger.warning(f"Duplicate key error for property: {item['id']}")
            raise DropItem(f"Duplicate item found: {item['id']}")
        except Exception as e:
            logger.error(f"Error saving property to MongoDB: {str(e)}")
            raise DropItem(f"Error processing item: {str(e)}")
            
    def _initialize_ml_model(self):
        """Initialize the machine learning model for investment analysis"""
        try:
            # Create and initialize the model
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
            
            # Try to load existing data to train the model
            properties = list(self.collection.find({
                'days_listed': {'$exists': True},
                'price_per_sqm': {'$exists': True},
                'size': {'$exists': True},
                'rooms': {'$exists': True}
            }))
            
            if len(properties) > 10:  # Only train if we have enough data
                # Prepare training data
                X = []
                y = []
                
                for prop in properties:
                    if prop.get('days_listed') is not None and prop.get('price_per_sqm') is not None:
                        features = [
                            prop.get('price_per_sqm', 0),
                            prop.get('size', 0),
                            prop.get('rooms', 0),
                            prop.get('bathrooms', 0),
                            1 if prop.get('has_elevator') else 0,
                        ]
                        X.append(features)
                        
                        # Target is inversely related to days listed (quicker sales are better investments)
                        days = max(1, prop.get('days_listed', 30))  # Avoid division by zero
                        investment_score = 100 / days  # Higher score for quicker sales
                        y.append(investment_score)
                
                # Train the model
                if X and y:
                    X = np.array(X)
                    self.scaler.fit(X)
                    X_scaled = self.scaler.transform(X)
                    self.ml_model.fit(X_scaled, y)
                    logger.info(f"Trained investment analysis model on {len(X)} properties")
            else:
                logger.info("Not enough data to train investment model. Will use default scoring.")
        except Exception as e:
            logger.error(f"Error initializing ML model: {str(e)}")
            self.ml_model = None
            
    def _analyze_investment_potential(self, item):
        """
        Analyze the investment potential of a property.
        Uses ML model if available, otherwise uses a simple heuristic.
        """
        try:
            # Calculate investment score
            if self.ml_model and self.scaler and 'price_per_sqm' in item:
                # Use ML model to predict score
                features = [
                    item.get('price_per_sqm', 0),
                    item.get('size', 0),
                    item.get('rooms', 0),
                    item.get('bathrooms', 0),
                    1 if item.get('has_elevator') else 0,
                ]
                
                features = np.array([features])
                features_scaled = self.scaler.transform(features)
                score = self.ml_model.predict(features_scaled)[0]
                
                # Normalize score to 0-100 range
                score = min(100, max(0, score))
                item['investment_score'] = round(score, 2)
            else:
                # Use simple heuristic
                # Better investment = lower price per sqm
                if 'price_per_sqm' in item:
                    # Find average price per sqm in the same area
                    area_query = {}
                    if 'city' in item and 'neighborhood' in item:
                        area_query = {
                            'city': item['city'],
                            'neighborhood': item['neighborhood'],
                            'price_per_sqm': {'$exists': True}
                        }
                    elif 'city' in item:
                        area_query = {
                            'city': item['city'],
                            'price_per_sqm': {'$exists': True}
                        }
                    
                    if area_query:
                        similar_properties = list(self.collection.find(area_query))
                        if similar_properties:
                            avg_price_per_sqm = sum(p.get('price_per_sqm', 0) for p in similar_properties) / len(similar_properties)
                            
                            # Calculate score: better if price is below average
                            ratio = item['price_per_sqm'] / avg_price_per_sqm if avg_price_per_sqm > 0 else 1
                            
                            # Score is inversely proportional to the price ratio
                            # < 1 means cheaper than average, > 1 means more expensive
                            score = min(100, max(0, 100 * (2 - ratio)))
                            item['investment_score'] = round(score, 2)
                        else:
                            item['investment_score'] = 50  # Default neutral score
                    else:
                        item['investment_score'] = 50  # Default neutral score
                else:
                    item['investment_score'] = 50  # Default neutral score
                    
            # Find comparable properties
            if 'city' in item and 'price' in item and 'size' in item:
                # Find properties in the same city with similar size (±20%) and price (±20%)
                size_range = (item['size'] * 0.8, item['size'] * 1.2)
                price_range = (item['price'] * 0.8, item['price'] * 1.2)
                
                comparable_query = {
                    'city': item['city'],
                    'size': {'$gte': size_range[0], '$lte': size_range[1]},
                    'price': {'$gte': price_range[0], '$lte': price_range[1]},
                    'id': {'$ne': item['id']}  # Exclude the current property
                }
                
                comparable_properties = list(self.collection.find(comparable_query, {'id': 1, 'source': 1, 'price': 1, 'size': 1, 'days_listed': 1}))
                
                # Store only the IDs and basic info of comparable properties
                item['comparable_properties'] = [
                    {
                        'id': p['id'],
                        'source': p['source'],
                        'price': p['price'],
                        'size': p['size'],
                        'days_listed': p.get('days_listed', 0)
                    }
                    for p in comparable_properties[:10]  # Limit to 10 comparable properties
                ]
                
        except Exception as e:
            logger.error(f"Error analyzing investment potential: {str(e)}")
            item['investment_score'] = 50  # Default neutral score
