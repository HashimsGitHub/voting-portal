"""
Election Service
Handles business logic for elections and voting
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from ..repositories.election_repository import ElectionRepository
from ..models.election import Election, Candidate, Vote, VotingRecord, ElectionStatus

logger = logging.getLogger(__name__)

class ElectionService:
    """Service for election operations"""
    
    def __init__(self, repository: ElectionRepository):
        self.repository = repository

    def create_election(self, title: str, description: str, total_seats: int = 10, 
                       start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a new election"""
        try:
            election = Election(
                title=title,
                description=description,
                status=ElectionStatus.DRAFT,
                total_seats=total_seats,
                start_date=start_date,
                end_date=end_date
            )
            
            election_id = self.repository.create_election(election.to_dict())
            
            return {
                "success": True,
                "election_id": election_id,
                "message": f"Election '{title}' created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating election: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_election_details(self, election_id: str) -> Dict[str, Any]:
        """Get election details with candidates and results"""
        try:
            election = self.repository.get_election(election_id)
            if not election:
                return {"success": False, "error": "Election not found"}
            
            candidates = self.repository.get_candidates_by_election(election_id)
            voter_stats = self.repository.get_election_voter_count(election_id)
            
            return {
                "success": True,
                "election": {
                    "_id": str(election["_id"]),
                    "title": election.get("title"),
                    "description": election.get("description"),
                    "status": election.get("status"),
                    "total_seats": election.get("total_seats"),
                    "start_date": election.get("start_date"),
                    "end_date": election.get("end_date"),
                    "created_at": election.get("created_at"),
                    "updated_at": election.get("updated_at")
                },
                "candidates": [
                    {
                        "_id": str(c["_id"]),
                        "name": c.get("name"),
                        "position": c.get("position"),
                        "bio": c.get("bio"),
                        "image_url": c.get("image_url"),
                        "batch_year": c.get("batch_year"),
                        "department": c.get("department"),
                        "vote_count": c.get("vote_count", 0)
                    }
                    for c in candidates
                ],
                "voter_stats": voter_stats
            }
        except Exception as e:
            logger.error(f"Error getting election details: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def add_candidate(self, election_id: str, name: str, position: str, 
                     bio: str, image_url: Optional[str] = None,
                     batch_year: Optional[int] = None,
                     department: Optional[str] = None,
                     contact_email: Optional[str] = None,
                     platform: Optional[str] = None) -> Dict[str, Any]:
        """Add a candidate to an election"""
        try:
            candidate = Candidate(
                name=name,
                position=position,
                bio=bio,
                image_url=image_url,
                batch_year=batch_year,
                department=department,
                contact_email=contact_email,
                platform=platform,
                election_id=election_id
            )
            
            candidate_id = self.repository.create_candidate(candidate.to_dict())
            
            return {
                "success": True,
                "candidate_id": candidate_id,
                "message": f"Candidate '{name}' added successfully"
            }
        except Exception as e:
            logger.error(f"Error adding candidate: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_candidates(self, election_id: str, position: Optional[str] = None) -> Dict[str, Any]:
        """Get candidates for an election"""
        try:
            if position:
                candidates = self.repository.get_candidates_by_position(election_id, position)
            else:
                candidates = self.repository.get_candidates_by_election(election_id)
            
            return {
                "success": True,
                "candidates": [
                    {
                        "_id": str(c["_id"]),
                        "name": c.get("name"),
                        "position": c.get("position"),
                        "bio": c.get("bio"),
                        "image_url": c.get("image_url"),
                        "batch_year": c.get("batch_year"),
                        "department": c.get("department"),
                        "contact_email": c.get("contact_email"),
                        "platform": c.get("platform"),
                        "vote_count": c.get("vote_count", 0)
                    }
                    for c in candidates
                ]
            }
        except Exception as e:
            logger.error(f"Error getting candidates: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def cast_vote(self, election_id: str, candidate_id: str, voter_id: str, 
                 voter_email: str) -> Dict[str, Any]:
        """Cast a vote"""
        try:
            # Check if voter has already voted
            if self.repository.has_voter_voted(election_id, voter_id):
                return {
                    "success": False,
                    "error": "You have already voted in this election"
                }
            
            # Verify election exists
            election = self.repository.get_election(election_id)
            if not election:
                return {
                    "success": False,
                    "error": "Election not found"
                }
            
            # Verify candidate exists
            candidate = self.repository.get_candidate(candidate_id)
            if not candidate:
                return {
                    "success": False,
                    "error": "Candidate not found"
                }
            
            # Cast the vote
            self.repository.cast_vote(election_id, candidate_id, voter_id, voter_email)
            
            return {
                "success": True,
                "message": f"Vote recorded for {candidate.get('name')}"
            }
        except Exception as e:
            logger.error(f"Error casting vote: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_live_results(self, election_id: str) -> Dict[str, Any]:
        """Get live election results"""
        try:
            results = self.repository.get_election_results(election_id)
            voter_stats = self.repository.get_election_voter_count(election_id)
            
            if "error" in results:
                return {
                    "success": False,
                    "error": results["error"]
                }
            
            # Add voter statistics
            results["voter_stats"] = voter_stats
            results["success"] = True
            
            return results
        except Exception as e:
            logger.error(f"Error getting results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_position_results(self, election_id: str, position: str) -> Dict[str, Any]:
        """Get live results for a specific position"""
        try:
            results = self.repository.get_position_results(election_id, position)
            
            if "error" in results:
                return {
                    "success": False,
                    "error": results["error"]
                }
            
            results["success"] = True
            return results
        except Exception as e:
            logger.error(f"Error getting position results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def activate_election(self, election_id: str) -> Dict[str, Any]:
        """Activate an election"""
        try:
            success = self.repository.update_election(election_id, {
                "status": ElectionStatus.ACTIVE.value
            })
            
            if success:
                return {
                    "success": True,
                    "message": "Election activated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to activate election"
                }
        except Exception as e:
            logger.error(f"Error activating election: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def close_election(self, election_id: str) -> Dict[str, Any]:
        """Close an election"""
        try:
            success = self.repository.update_election(election_id, {
                "status": ElectionStatus.CLOSED.value
            })
            
            if success:
                return {
                    "success": True,
                    "message": "Election closed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to close election"
                }
        except Exception as e:
            logger.error(f"Error closing election: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def register_voter(self, election_id: str, voter_id: str, voter_email: str) -> Dict[str, Any]:
        """Register a voter for an election"""
        try:
            success = self.repository.create_voting_record(election_id, voter_id, voter_email)
            
            if success:
                return {
                    "success": True,
                    "message": "Voter registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to register voter"
                }
        except Exception as e:
            logger.error(f"Error registering voter: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
