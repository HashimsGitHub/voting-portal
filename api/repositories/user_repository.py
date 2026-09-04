"""
User Repository
Handles MongoDB operations for authentication accounts
"""
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user authentication data"""

    def __init__(self, mongo_connection_string: str):
        try:
            self.client = MongoClient(mongo_connection_string)
            self.db = self.client['voting_portal']
            self.users_collection = self.db['users']
            self.users_collection.create_index("email", unique=True)
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user account"""
        result = self.users_collection.insert_one(user_data)
        logger.info(f"User created: {result.inserted_id}")
        return str(result.inserted_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Look up a user by email"""
        try:
            return self.users_collection.find_one({"email": email})
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Look up a user by id"""
        try:
            from bson import ObjectId
            return self.users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Error getting user by id: {str(e)}")
            return None

    def get_all_users(self, role: Optional[str] = None) -> list:
        """List user accounts, optionally filtered by role"""
        try:
            query = {"role": role} if role else {}
            return list(self.users_collection.find(query).sort("created_at", -1))
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []

    def count_users(self, role: Optional[str] = None) -> int:
        """Count user accounts, optionally filtered by role"""
        try:
            query = {"role": role} if role else {}
            return self.users_collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting users: {str(e)}")
            return 0

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a user account"""
        try:
            from bson import ObjectId
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """Delete a user account"""
        try:
            from bson import ObjectId
            result = self.users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
