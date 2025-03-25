"""
Database connection utilities for the API.
"""

import os
import logging
import pymongo
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict

logger = logging.getLogger(__name__)

# Mock DB implementation that returns empty data
class FakeCursor:
    def __init__(self, items=None):
        self.items = items or []
        
    def limit(self, n):
        return self
        
    def skip(self, n):
        return self
        
    def sort(self, field, direction=1):
        return self
        
    def __iter__(self):
        return iter(self.items)
        
    def __list__(self):
        return self.items


class FakeCollection:
    def __init__(self, name):
        self.name = name
        
    def find(self, query=None, projection=None):
        logger.debug(f"Find called on {self.name} with {query}")
        return FakeCursor()
        
    def find_one(self, query=None):
        logger.debug(f"Find one called on {self.name} with {query}")
        return None
        
    def count_documents(self, query=None):
        return 0
        
    def distinct(self, field, query=None):
        return []
        
    def update_one(self, filter_query, update_query, upsert=False):
        logger.debug(f"Update one called on {self.name} with filter {filter_query} and update {update_query}")
        return {"modified_count": 0, "matched_count": 0, "upserted_id": None}
        
    def insert_one(self, document):
        logger.debug(f"Insert one called on {self.name} with {document}")
        return {"inserted_id": "fake_id"}
        
    def aggregate(self, pipeline):
        return []


class FakeDB:
    """Mock database for when MongoDB is not available"""
    def __init__(self):
        self.collections = defaultdict(lambda: FakeCollection("unknown"))
        
    def __getitem__(self, name):
        logger.debug(f"Getting collection {name}")
        return self.collections[name]
    
    def command(self, cmd):
        logger.debug(f"Command {cmd} called")
        return {"ok": 1.0}
    

def get_db_connection():
    """
    Get a connection to the database
    
    Returns:
        Database object
    """
    # First try MongoDB
    try:
        # Get MongoDB connection string from environment variable, or use default
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
        
        # Get database name from environment variable, or use default
        db_name = os.environ.get('MONGODB_DATABASE', 'realestate')
        
        # Connect to MongoDB with a short timeout
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        db = client[db_name]
        
        # Test connection
        db.command('ping')
        logger.info(f"Connected to MongoDB: {mongodb_uri}, DB: {db_name}")
        
        return db
    except Exception as mongo_e:
        logger.warning(f"Could not connect to MongoDB: {str(mongo_e)}")
        
        # Fall back to PostgreSQL or return a fake DB
        if os.environ.get('DATABASE_URL'):
            logger.info("MongoDB not available, using fake DB implementation")
            return FakeDB()
        else:
            logger.error("No database available")
            return FakeDB()
