from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema

class ReviewBase(BaseSchema):
    agent_id: int
    reviewer_id: int
    rating: Decimal = Field(..., ge=0, le=5, description="Rating from 0 to 5")
    comment: str = Field(..., min_length=10, max_length=1000)
    usage_context: Optional[str] = Field(None, max_length=200)

    @validator('rating')
    def validate_rating(cls, v):
        return round(float(v), 1)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseSchema):
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)
    usage_context: Optional[str] = Field(None, max_length=200)

class Review(ReviewBase, TimestampedSchema):
    id: int
    agent_creator_id: int
    is_verified_purchase: bool = False
    is_edited: bool = False
    usage_duration: Optional[int] = None

class ReviewWithRelations(Review):
    reviewer: "UserPublic"
    agent: "AgentList"

from .user import UserPublic
from .agent import AgentList