"""
Position (Seat) Model
Admin-managed seats/positions that candidates can run for (e.g. President, VP East Region)
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Position:
    """A seat/position within an election, created and managed by admins"""
    def __init__(self,
                 name: str,
                 election_id: str,
                 region: Optional[str] = None,
                 description: Optional[str] = None,
                 _id: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self._id = _id or str(ObjectId())
        self.name = name
        self.election_id = election_id
        self.region = region
        self.description = description
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "election_id": self.election_id,
            "region": self.region,
            "description": self.description,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        return Position(
            name=data.get("name"),
            election_id=data.get("election_id"),
            region=data.get("region"),
            description=data.get("description"),
            _id=str(data.get("_id", ObjectId())),
            created_at=data.get("created_at", datetime.utcnow())
        )
