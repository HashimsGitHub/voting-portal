#!/usr/bin/env python3
"""
Database Initialization Script
Creates MongoDB collections and indexes for the voting portal
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
if not MONGODB_CONNECTION_STRING:
    logger.error("MONGODB_CONNECTION_STRING not found in environment variables")
    sys.exit(1)

def init_database():
    """Initialize MongoDB collections and indexes"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client['voting_portal']
        
        logger.info("Connected to MongoDB successfully")
        
        # Create elections collection
        if 'elections' not in db.list_collection_names():
            db.create_collection('elections')
            logger.info("Created 'elections' collection")
        
        # Create candidates collection
        if 'candidates' not in db.list_collection_names():
            db.create_collection('candidates')
            logger.info("Created 'candidates' collection")
        
        # Create votes collection
        if 'votes' not in db.list_collection_names():
            db.create_collection('votes')
            logger.info("Created 'votes' collection")
        
        # Create voting_records collection
        if 'voting_records' not in db.list_collection_names():
            db.create_collection('voting_records')
            logger.info("Created 'voting_records' collection")
        
        # Create indexes
        elections = db['elections']
        elections.create_index('title')
        elections.create_index('status')
        logger.info("Created indexes for 'elections' collection")
        
        candidates = db['candidates']
        candidates.create_index('election_id')
        candidates.create_index('position')
        candidates.create_index([('election_id', 1), ('position', 1)])
        logger.info("Created indexes for 'candidates' collection")
        
        votes = db['votes']
        votes.create_index('election_id')
        votes.create_index('candidate_id')
        votes.create_index('voter_id')
        votes.create_index([('election_id', 1), ('voter_id', 1)], unique=True)
        logger.info("Created indexes for 'votes' collection")
        
        voting_records = db['voting_records']
        voting_records.create_index([('election_id', 1), ('voter_id', 1)], unique=True)
        logger.info("Created indexes for 'voting_records' collection")
        
        logger.info("✅ Database initialization completed successfully!")
        
        # Print collection info
        logger.info(f"Collections created: {db.list_collection_names()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
