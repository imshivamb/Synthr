from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
from .base import BaseSchema, TimestampedSchema
from ..models.agent import AgentStatus, AgentCategory

class AgentBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    category: AgentCategory
    price: Decimal = Field(..., ge=0)
    capabilities: List[str] = Field(..., min_items=1)
    metadata: Dict = Field(default_factory=dict)

class AgentCreate(AgentBase):
    creator_id: int
    model_parameters: Dict = Field(...)

class AgentUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class AgentInDBBase(AgentBase, TimestampedSchema):
    id: int
    token_id: str
    creator_id: int
    owner_id: int
    status: AgentStatus
    is_listed: bool
    ipfs_hash: Optional[str]
    total_uses: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0

class Agent(AgentInDBBase):
    pass

class AgentWithRelations(Agent):
    creator: "UserPublic"
    owner: "UserPublic"
    model: Optional["AIModel"] = None
    reviews: List["Review"] = []

class AgentList(BaseSchema):
    id: int
    name: str
    description: str
    price: Decimal
    category: AgentCategory
    status: AgentStatus
    average_rating: float
    total_ratings: int
    creator: "UserPublic"

from .user import UserPublic  # Prevent circular import