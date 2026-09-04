"""
Election Service
Handles business logic for elections and voting
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from repositories.election_repository import ElectionRepository
from models.election import Election, Candidate, Vote, VotingRecord, ElectionStatus
from models.position import Position

MAX_POSITIONS_PER_CANDIDATE = 3

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
                        "positions": c.get("positions", []),
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

    def get_stats(self, election_id: str, total_registered_voters: int) -> Dict[str, Any]:
        """Aggregate headline numbers for the public dashboard"""
        try:
            election = self.repository.get_election(election_id)
            if not election:
                return {"success": False, "error": "Election not found"}

            positions = self.repository.get_positions_by_election(election_id)
            candidates = self.repository.get_candidates_by_election(election_id)
            voter_stats = self.repository.get_election_voter_count(election_id)

            return {
                "success": True,
                "stats": {
                    "total_seats": len(positions) or election.get("total_seats", 0),
                    "total_candidates": len(candidates),
                    "total_registered_voters": total_registered_voters,
                    "total_votes_cast": voter_stats.get("total_voted", 0),
                    "turnout_percentage": voter_stats.get("turnout_percentage", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"success": False, "error": str(e)}

    def self_register_candidate(self, election_id: str, user_id: str, name: str, contact_email: str) -> Dict[str, Any]:
        """Create a bare candidate profile for a self-registered candidate account.

        No positions/seats yet - admins assign those separately, since seat
        eligibility (e.g. region) is an admin-controlled decision.
        """
        try:
            candidate = Candidate(
                name=name,
                positions=[],
                bio="",
                contact_email=contact_email,
                user_id=user_id,
                election_id=election_id
            )
            candidate_id = self.repository.create_candidate(candidate.to_dict())
            return {"success": True, "candidate_id": candidate_id}
        except Exception as e:
            logger.error(f"Error self-registering candidate: {str(e)}")
            return {"success": False, "error": str(e)}

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
                        "positions": c.get("positions", []),
                        "bio": c.get("bio"),
                        "image_url": c.get("image_url"),
                        "batch_year": c.get("batch_year"),
                        "department": c.get("department"),
                        "contact_email": c.get("contact_email"),
                        "platform": c.get("platform"),
                        "profile_url": c.get("profile_url"),
                        "linkedin_url": c.get("linkedin_url"),
                        "social_url": c.get("social_url"),
                        "campaign_media": c.get("campaign_media", []),
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

    def get_my_candidate_profile(self, user_id: str) -> Dict[str, Any]:
        """Get the candidate profile linked to a candidate user account"""
        try:
            candidate = self.repository.get_candidate_by_user_id(user_id)
            if not candidate:
                return {"success": False, "error": "No candidate profile is linked to this account yet"}

            election = self.repository.get_election(candidate.get("election_id"))

            return {
                "success": True,
                "candidate": {
                    "_id": str(candidate["_id"]),
                    "name": candidate.get("name"),
                    "positions": candidate.get("positions", []),
                    "bio": candidate.get("bio"),
                    "image_url": candidate.get("image_url"),
                    "profile_url": candidate.get("profile_url"),
                    "linkedin_url": candidate.get("linkedin_url"),
                    "social_url": candidate.get("social_url"),
                    "campaign_media": candidate.get("campaign_media", []),
                    "election_id": candidate.get("election_id"),
                    "election_status": election.get("status") if election else None,
                    "vote_count": candidate.get("vote_count", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error getting candidate profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def update_my_candidate_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Let a candidate edit their own photo, bio, profile URL and the seats they run for.

        Candidates pick their own seats (max 3), but only while the election is still
        in draft - once an admin opens the election, seat selection locks and only an
        admin can change it (e.g. to correct a mistake).
        """
        try:
            candidate = self.repository.get_candidate_by_user_id(user_id)
            if not candidate:
                return {"success": False, "error": "No candidate profile is linked to this account yet"}

            editable_fields = {"image_url", "bio", "profile_url", "linkedin_url", "social_url", "positions"}
            allowed_updates = {k: v for k, v in updates.items() if k in editable_fields}

            if not allowed_updates:
                return {"success": False, "error": "No editable fields provided"}

            if "positions" in allowed_updates:
                positions = allowed_updates["positions"]
                if not positions or len(positions) == 0:
                    return {"success": False, "error": "You must select at least one position"}
                if len(positions) > MAX_POSITIONS_PER_CANDIDATE:
                    return {"success": False, "error": f"You can run for at most {MAX_POSITIONS_PER_CANDIDATE} positions"}

                election = self.repository.get_election(candidate.get("election_id"))
                if election and election.get("status") != ElectionStatus.DRAFT.value:
                    return {"success": False, "error": "Seats are locked once the election is open - ask an admin to change them"}

            success = self.repository.update_candidate(str(candidate["_id"]), allowed_updates)

            if success:
                return {"success": True, "message": "Profile updated successfully"}
            else:
                return {"success": False, "error": "Failed to update profile"}
        except Exception as e:
            logger.error(f"Error updating candidate profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def cast_vote(self, election_id: str, candidate_id: str, voter_id: str,
                 voter_email: str, position: str) -> Dict[str, Any]:
        """Cast a vote for a candidate in a specific position/seat.
        A voter may vote once per position, but not twice for the same position."""
        try:
            if not position:
                return {"success": False, "error": "Missing position"}

            # Check if voter has already voted for this position
            if self.repository.has_voter_voted(election_id, voter_id, position):
                return {
                    "success": False,
                    "error": "You have already voted for this position"
                }

            # Verify election exists and is active
            election = self.repository.get_election(election_id)
            if not election:
                return {
                    "success": False,
                    "error": "Election not found"
                }
            if election.get("status") != ElectionStatus.ACTIVE.value:
                return {
                    "success": False,
                    "error": "This election is not currently active"
                }

            # Verify candidate exists and is running for this position
            candidate = self.repository.get_candidate(candidate_id)
            if not candidate:
                return {
                    "success": False,
                    "error": "Candidate not found"
                }
            if position not in (candidate.get("positions") or []):
                return {
                    "success": False,
                    "error": f"{candidate.get('name')} is not running for {position}"
                }

            # Cast the vote
            self.repository.cast_vote(election_id, candidate_id, voter_id, voter_email, position)

            return {
                "success": True,
                "message": f"Vote recorded for {candidate.get('name')} ({position})"
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

    def open_nominations(self, election_id: str) -> Dict[str, Any]:
        """Reopen seat selection for candidates (election back to draft/nomination phase)"""
        try:
            success = self.repository.update_election(election_id, {
                "status": ElectionStatus.DRAFT.value
            })

            if success:
                return {
                    "success": True,
                    "message": "Candidates can now select their seats"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to open nominations"
                }
        except Exception as e:
            logger.error(f"Error opening nominations: {str(e)}")
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

    def close_election(self, election_id: str, force: bool = False) -> Dict[str, Any]:
        """Close an election. Admins can only close after the election's end date has passed,
        unless force=True is explicitly requested."""
        try:
            election = self.repository.get_election(election_id)
            if not election:
                return {"success": False, "error": "Election not found"}

            end_date = election.get("end_date")
            if not force and end_date and datetime.utcnow() < end_date:
                return {
                    "success": False,
                    "error": f"Cannot close this election before its end date ({end_date.strftime('%Y-%m-%d')})"
                }

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

    # ==================== POSITION (SEAT) OPERATIONS ====================

    def create_position(self, election_id: str, name: str, region: Optional[str] = None,
                       description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new position/seat for an election"""
        try:
            position = Position(name=name, election_id=election_id, region=region, description=description)
            position_id = self.repository.create_position(position.to_dict())
            return {
                "success": True,
                "position_id": position_id,
                "message": f"Position '{name}' created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating position: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_positions(self, election_id: str) -> Dict[str, Any]:
        """List positions/seats for an election"""
        try:
            positions = self.repository.get_positions_by_election(election_id)
            return {
                "success": True,
                "positions": [
                    {
                        "_id": str(p["_id"]),
                        "name": p.get("name"),
                        "region": p.get("region"),
                        "description": p.get("description")
                    }
                    for p in positions
                ]
            }
        except Exception as e:
            logger.error(f"Error listing positions: {str(e)}")
            return {"success": False, "error": str(e)}

    def update_position(self, position_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a position/seat's name, region or description"""
        try:
            editable_fields = {"name", "region", "description"}
            allowed_updates = {k: v for k, v in updates.items() if k in editable_fields}
            if not allowed_updates:
                return {"success": False, "error": "No editable fields provided"}

            success = self.repository.update_position(position_id, allowed_updates)
            if success:
                return {"success": True, "message": "Position updated successfully"}
            else:
                return {"success": False, "error": "Failed to update position"}
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
            return {"success": False, "error": str(e)}

    def delete_position(self, position_id: str) -> Dict[str, Any]:
        """Delete a position/seat"""
        try:
            position = self.repository.get_position(position_id)
            if not position:
                return {"success": False, "error": "Position not found"}

            candidates_using = self.repository.get_candidates_by_position(position["election_id"], position["name"])
            if candidates_using:
                return {
                    "success": False,
                    "error": f"Cannot delete '{position['name']}' - {len(candidates_using)} candidate(s) are running for it"
                }

            success = self.repository.delete_position(position_id)
            if success:
                return {"success": True, "message": "Position deleted successfully"}
            else:
                return {"success": False, "error": "Failed to delete position"}
        except Exception as e:
            logger.error(f"Error deleting position: {str(e)}")
            return {"success": False, "error": str(e)}

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
