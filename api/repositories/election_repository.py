"""
Election Repository
Handles all MongoDB operations for elections, candidates, and votes
"""
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
import logging

logger = logging.getLogger(__name__)

class ElectionRepository:
    """Repository for election operations"""
    
    def __init__(self, mongo_connection_string: str):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(mongo_connection_string)
            self.db = self.client['voting_portal']
            self.elections_collection: Collection = self.db['elections']
            self.candidates_collection: Collection = self.db['candidates']
            self.votes_collection: Collection = self.db['votes']
            self.voting_records_collection: Collection = self.db['voting_records']
            
            # Create indexes for better query performance
            self._create_indexes()
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def _create_indexes(self):
        """Create necessary indexes for collections"""
        try:
            # Elections indexes
            self.elections_collection.create_index("title")
            self.elections_collection.create_index("status")
            
            # Candidates indexes
            self.candidates_collection.create_index("election_id")
            self.candidates_collection.create_index("position")
            self.candidates_collection.create_index([("election_id", 1), ("position", 1)])
            
            # Votes indexes
            self.votes_collection.create_index("election_id")
            self.votes_collection.create_index("candidate_id")
            self.votes_collection.create_index("voter_id")
            self.votes_collection.create_index([("election_id", 1), ("voter_id", 1)], unique=True)
            
            # Voting records indexes
            self.voting_records_collection.create_index([("election_id", 1), ("voter_id", 1)], unique=True)
            
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")

    # ==================== ELECTION OPERATIONS ====================
    
    def create_election(self, election_data: Dict[str, Any]) -> str:
        """Create a new election"""
        try:
            result = self.elections_collection.insert_one(election_data)
            logger.info(f"Election created: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating election: {str(e)}")
            raise

    def get_election(self, election_id: str) -> Optional[Dict]:
        """Get election by ID"""
        try:
            return self.elections_collection.find_one({"_id": ObjectId(election_id)})
        except Exception as e:
            logger.error(f"Error getting election: {str(e)}")
            return None

    def get_all_elections(self, status: Optional[str] = None) -> List[Dict]:
        """Get all elections, optionally filtered by status"""
        try:
            query = {}
            if status:
                query["status"] = status
            return list(self.elections_collection.find(query).sort("created_at", -1))
        except Exception as e:
            logger.error(f"Error getting elections: {str(e)}")
            return []

    def update_election(self, election_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an election"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.elections_collection.update_one(
                {"_id": ObjectId(election_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating election: {str(e)}")
            return False

    def delete_election(self, election_id: str) -> bool:
        """Delete an election and related data"""
        try:
            # Delete related documents
            self.candidates_collection.delete_many({"election_id": election_id})
            self.votes_collection.delete_many({"election_id": election_id})
            self.voting_records_collection.delete_many({"election_id": election_id})
            
            # Delete election
            result = self.elections_collection.delete_one({"_id": ObjectId(election_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting election: {str(e)}")
            return False

    # ==================== CANDIDATE OPERATIONS ====================
    
    def create_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Create a new candidate"""
        try:
            result = self.candidates_collection.insert_one(candidate_data)
            logger.info(f"Candidate created: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating candidate: {str(e)}")
            raise

    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        """Get candidate by ID"""
        try:
            return self.candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        except Exception as e:
            logger.error(f"Error getting candidate: {str(e)}")
            return None

    def get_candidates_by_election(self, election_id: str) -> List[Dict]:
        """Get all candidates for an election"""
        try:
            candidates = list(self.candidates_collection.find({"election_id": election_id}))
            # Enrich with vote counts
            for candidate in candidates:
                vote_count = self.votes_collection.count_documents({"candidate_id": str(candidate["_id"])})
                candidate["vote_count"] = vote_count
            return candidates
        except Exception as e:
            logger.error(f"Error getting candidates: {str(e)}")
            return []

    def get_candidates_by_position(self, election_id: str, position: str) -> List[Dict]:
        """Get candidates for a specific position"""
        try:
            candidates = list(self.candidates_collection.find({
                "election_id": election_id,
                "position": position
            }))
            # Enrich with vote counts
            for candidate in candidates:
                vote_count = self.votes_collection.count_documents({"candidate_id": str(candidate["_id"])})
                candidate["vote_count"] = vote_count
            return candidates
        except Exception as e:
            logger.error(f"Error getting candidates by position: {str(e)}")
            return []

    def update_candidate(self, candidate_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a candidate"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.candidates_collection.update_one(
                {"_id": ObjectId(candidate_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating candidate: {str(e)}")
            return False

    def delete_candidate(self, candidate_id: str) -> bool:
        """Delete a candidate and related votes"""
        try:
            candidate_id_str = str(candidate_id)
            self.votes_collection.delete_many({"candidate_id": candidate_id_str})
            result = self.candidates_collection.delete_one({"_id": ObjectId(candidate_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting candidate: {str(e)}")
            return False

    # ==================== VOTING OPERATIONS ====================
    
    def cast_vote(self, election_id: str, candidate_id: str, voter_id: str, voter_email: str) -> bool:
        """Record a vote"""
        try:
            vote_data = {
                "election_id": election_id,
                "candidate_id": candidate_id,
                "voter_id": voter_id,
                "voter_email": voter_email,
                "created_at": datetime.utcnow()
            }
            self.votes_collection.insert_one(vote_data)
            
            # Update voting record
            self.voting_records_collection.update_one(
                {"election_id": election_id, "voter_id": voter_id},
                {
                    "$set": {
                        "has_voted": True,
                        "voted_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Vote recorded for candidate {candidate_id}")
            return True
        except Exception as e:
            logger.error(f"Error casting vote: {str(e)}")
            raise

    def has_voter_voted(self, election_id: str, voter_id: str) -> bool:
        """Check if a voter has already voted"""
        try:
            vote = self.votes_collection.find_one({
                "election_id": election_id,
                "voter_id": voter_id
            })
            return vote is not None
        except Exception as e:
            logger.error(f"Error checking voter status: {str(e)}")
            return False

    def get_election_results(self, election_id: str) -> Dict[str, Any]:
        """Get election results with vote counts per candidate"""
        try:
            candidates = self.get_candidates_by_election(election_id)
            total_votes = self.votes_collection.count_documents({"election_id": election_id})
            
            results = {
                "election_id": election_id,
                "total_votes": total_votes,
                "candidates": []
            }
            
            for candidate in candidates:
                candidate_id = str(candidate["_id"])
                vote_count = self.votes_collection.count_documents({
                    "election_id": election_id,
                    "candidate_id": candidate_id
                })
                
                results["candidates"].append({
                    "candidate_id": candidate_id,
                    "name": candidate.get("name"),
                    "position": candidate.get("position"),
                    "bio": candidate.get("bio"),
                    "image_url": candidate.get("image_url"),
                    "vote_count": vote_count,
                    "vote_percentage": (vote_count / total_votes * 100) if total_votes > 0 else 0
                })
            
            # Sort by vote count
            results["candidates"].sort(key=lambda x: x["vote_count"], reverse=True)
            
            return results
        except Exception as e:
            logger.error(f"Error getting results: {str(e)}")
            return {"error": str(e)}

    def get_position_results(self, election_id: str, position: str) -> Dict[str, Any]:
        """Get results for a specific position"""
        try:
            candidates = self.get_candidates_by_position(election_id, position)
            total_votes = self.votes_collection.count_documents({
                "election_id": election_id,
                "candidate_id": {"$in": [str(c["_id"]) for c in candidates]}
            })
            
            results = {
                "election_id": election_id,
                "position": position,
                "total_votes": total_votes,
                "candidates": []
            }
            
            for candidate in candidates:
                candidate_id = str(candidate["_id"])
                vote_count = self.votes_collection.count_documents({
                    "election_id": election_id,
                    "candidate_id": candidate_id
                })
                
                results["candidates"].append({
                    "candidate_id": candidate_id,
                    "name": candidate.get("name"),
                    "bio": candidate.get("bio"),
                    "image_url": candidate.get("image_url"),
                    "vote_count": vote_count,
                    "vote_percentage": (vote_count / total_votes * 100) if total_votes > 0 else 0
                })
            
            results["candidates"].sort(key=lambda x: x["vote_count"], reverse=True)
            
            return results
        except Exception as e:
            logger.error(f"Error getting position results: {str(e)}")
            return {"error": str(e)}

    # ==================== VOTING RECORD OPERATIONS ====================
    
    def create_voting_record(self, election_id: str, voter_id: str, voter_email: str) -> bool:
        """Create a voting record for a voter"""
        try:
            record_data = {
                "election_id": election_id,
                "voter_id": voter_id,
                "voter_email": voter_email,
                "has_voted": False,
                "voted_at": None
            }
            self.voting_records_collection.insert_one(record_data)
            return True
        except Exception as e:
            logger.error(f"Error creating voting record: {str(e)}")
            return False

    def get_voting_record(self, election_id: str, voter_id: str) -> Optional[Dict]:
        """Get voting record for a voter"""
        try:
            return self.voting_records_collection.find_one({
                "election_id": election_id,
                "voter_id": voter_id
            })
        except Exception as e:
            logger.error(f"Error getting voting record: {str(e)}")
            return None

    def get_election_voter_count(self, election_id: str) -> Dict[str, int]:
        """Get voter statistics for an election"""
        try:
            total_registered = self.voting_records_collection.count_documents(
                {"election_id": election_id}
            )
            total_voted = self.voting_records_collection.count_documents({
                "election_id": election_id,
                "has_voted": True
            })
            
            return {
                "total_registered": total_registered,
                "total_voted": total_voted,
                "turnout_percentage": (total_voted / total_registered * 100) if total_registered > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting voter count: {str(e)}")
            return {}
