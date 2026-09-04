"""
Election Models
Handles candidates, elections, votes, and voting records
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from bson import ObjectId

class ElectionStatus(str, Enum):
    """Election status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    COMPLETED = "completed"

class Candidate:
    """Candidate model for elections"""
    def __init__(self,
                 name: str,
                 positions: List[str],
                 bio: str,
                 image_url: Optional[str] = None,
                 batch_year: Optional[int] = None,
                 department: Optional[str] = None,
                 contact_email: Optional[str] = None,
                 platform: Optional[str] = None,
                 profile_url: Optional[str] = None,
                 linkedin_url: Optional[str] = None,
                 social_url: Optional[str] = None,
                 campaign_media: Optional[List[dict]] = None,
                 user_id: Optional[str] = None,
                 election_id: Optional[str] = None,
                 _id: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self._id = _id or str(ObjectId())
        self.name = name
        self.positions = positions or []
        self.bio = bio
        self.image_url = image_url
        self.batch_year = batch_year
        self.department = department
        self.contact_email = contact_email.strip().lower() if contact_email else contact_email
        self.platform = platform
        self.profile_url = profile_url
        self.linkedin_url = linkedin_url
        self.social_url = social_url
        self.campaign_media = campaign_media or []
        self.user_id = user_id
        self.election_id = election_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.vote_count = 0

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "positions": self.positions,
            "bio": self.bio,
            "image_url": self.image_url,
            "batch_year": self.batch_year,
            "department": self.department,
            "contact_email": self.contact_email,
            "platform": self.platform,
            "profile_url": self.profile_url,
            "linkedin_url": self.linkedin_url,
            "social_url": self.social_url,
            "campaign_media": self.campaign_media,
            "user_id": self.user_id,
            "election_id": self.election_id,
            "vote_count": self.vote_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict):
        return Candidate(
            name=data.get("name"),
            positions=data.get("positions", []),
            bio=data.get("bio"),
            image_url=data.get("image_url"),
            batch_year=data.get("batch_year"),
            department=data.get("department"),
            contact_email=data.get("contact_email"),
            platform=data.get("platform"),
            profile_url=data.get("profile_url"),
            linkedin_url=data.get("linkedin_url"),
            social_url=data.get("social_url"),
            campaign_media=data.get("campaign_media"),
            user_id=data.get("user_id"),
            election_id=data.get("election_id"),
            _id=str(data.get("_id", ObjectId())),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )


class Election:
    """Election model"""
    def __init__(self,
                 title: str,
                 description: str,
                 status: ElectionStatus = ElectionStatus.DRAFT,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 total_seats: int = 10,
                 _id: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self._id = _id or str(ObjectId())
        self.title = title
        self.description = description
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.total_seats = total_seats
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, ElectionStatus) else self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_seats": self.total_seats,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict):
        status = data.get("status", ElectionStatus.DRAFT)
        if isinstance(status, str):
            status = ElectionStatus(status)
        
        return Election(
            title=data.get("title"),
            description=data.get("description"),
            status=status,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            total_seats=data.get("total_seats", 10),
            _id=str(data.get("_id", ObjectId())),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )


class Vote:
    """Vote model for tracking votes"""
    def __init__(self,
                 election_id: str,
                 candidate_id: str,
                 voter_id: str,
                 voter_email: str,
                 _id: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self._id = _id or str(ObjectId())
        self.election_id = election_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.voter_email = voter_email
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "election_id": self.election_id,
            "candidate_id": self.candidate_id,
            "voter_id": self.voter_id,
            "voter_email": self.voter_email,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return Vote(
            election_id=data.get("election_id"),
            candidate_id=data.get("candidate_id"),
            voter_id=data.get("voter_id"),
            voter_email=data.get("voter_email"),
            _id=str(data.get("_id", ObjectId())),
            created_at=data.get("created_at", datetime.utcnow())
        )


class VotingRecord:
    """Track voting participation"""
    def __init__(self,
                 election_id: str,
                 voter_id: str,
                 voter_email: str,
                 has_voted: bool = False,
                 _id: Optional[str] = None,
                 voted_at: Optional[datetime] = None):
        self._id = _id or str(ObjectId())
        self.election_id = election_id
        self.voter_id = voter_id
        self.voter_email = voter_email
        self.has_voted = has_voted
        self.voted_at = voted_at

    def to_dict(self):
        return {
            "_id": self._id,
            "election_id": self.election_id,
            "voter_id": self.voter_id,
            "voter_email": self.voter_email,
            "has_voted": self.has_voted,
            "voted_at": self.voted_at
        }

    @staticmethod
    def from_dict(data: dict):
        return VotingRecord(
            election_id=data.get("election_id"),
            voter_id=data.get("voter_id"),
            voter_email=data.get("voter_email"),
            has_voted=data.get("has_voted", False),
            _id=str(data.get("_id", ObjectId())),
            voted_at=data.get("voted_at")
        )
