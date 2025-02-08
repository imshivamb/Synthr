from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime
from .base import BaseSchema

# Wallet Auth

class WalletConnectRequest(BaseSchema):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    chain_id: int

class WalletSignatureRequest(BaseSchema):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    signature: str
    nonce: str

#Oauth Auth

class OAuthRequest(BaseSchema):
    provider: Literal["google", "github", "discord"]
    code: str
    redirect_uri: str

class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None
    
class TokenPayload(BaseSchema):
    sub: str  # wallet_address or oauth_id
    exp: datetime
    auth_method: Literal["wallet", "oauth"]
    provider: Optional[str] = None

#Respose Schema

class AuthResponse(BaseSchema):
    token: Token
    user: dict
    
# Session Management
class RefreshTokenRequest(BaseSchema):
    refresh_token: str

class RevokeTokenRequest(BaseSchema):
    token: str

# OAuth Profile
class OAuthProfile(BaseSchema):
    provider: str
    provider_user_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

# Link Accounts
class LinkWalletRequest(BaseSchema):
    wallet_address: str
    oauth_provider: str
    oauth_token: str