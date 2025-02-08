from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema
from ..models.agent import AgentCategory, AgentStatus

class DateRangeFilter(BaseSchema):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PriceRangeFilter(BaseSchema):
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = None

class AgentFilter(BaseSchema):
    category: Optional[AgentCategory] = None
    status: Optional[AgentStatus] = None
    creator_address: Optional[str] = None
    price_range: Optional[PriceRangeFilter] = None
    date_range: Optional[DateRangeFilter] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)

class TransactionFilter(BaseSchema):
    buyer_address: Optional[str] = None
    seller_address: Optional[str] = None
    status: Optional[str] = None
    date_range: Optional[DateRangeFilter] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = None

class ReviewFilter(BaseSchema):
    agent_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    verified_only: bool = False
    date_range: Optional[DateRangeFilter] = None

class TrainingFilter(BaseSchema):
    status: Optional[str] = None
    model_type: Optional[str] = None
    creator_id: Optional[int] = None
    date_range: Optional[DateRangeFilter] = None