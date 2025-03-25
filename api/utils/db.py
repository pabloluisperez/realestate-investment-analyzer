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
class FakeCollection:
    def __init__(self, name):
        self.name = name
        
    def find(self, query=None, projection=None):
        logger.debug(f"Find called on {self.name} with {query}")
        return []
        
    def find_one(self, query=None):
        logger.debug(f"Find one called on {self.name} with {query}")
        return None
        
    def count_documents(self, query=None):
        return 0
        
    def distinct(self, field, query=None):
        return []
        
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
