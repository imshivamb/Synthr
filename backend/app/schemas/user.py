from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Literal
from .base import BaseSchema, TimestampedSchema

class OAuthAccountBase(BaseSchema):
    provider: str
    provider_user_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserBase(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = Field(None, min_length=42, max_length=42)
    reputation_score: int = 0

class UserCreate(UserBase):
    auth_method: Literal["wallet", "oauth"]
    oauth_data: Optional[OAuthAccountBase] = None

class UserUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    profile: Optional[Dict] = None
    preferences: Optional[Dict] = None

class UserInDBBase(UserBase, TimestampedSchema):
    id: int
    is_active: bool = True
    is_verified: bool = False
    profile: Dict = {}
    preferences: Dict = {}
    oauth_accounts: List[OAuthAccountBase] = []

class User(UserInDBBase):
    pass

class UserWithStats(User):
    total_agents_created: int = 0
    total_agents_owned: int = 0
    total_transactions: int = 0
    average_rating: float = 0.0

class UserPublic(BaseSchema):
    id: int
    username: Optional[str]
    wallet_address: Optional[str]
    reputation_score: int
    profile: Dict