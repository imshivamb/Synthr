from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db, get_current_user
from app.core.security import create_nonce, create_access_token, verify_wallet_ownership
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from typing import Any
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class WalletRequest(BaseModel):
    wallet_address: str

class SignatureRequest(BaseModel):
    wallet_address: str
    signature: str

@router.post("/nonce", response_model=dict)
async def get_nonce(
    request: WalletRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a nonce for wallet signature.
    """
    # Create or get user
    user = db.query(User).filter(User.wallet_address == request.wallet_address).first()
    if not user:
        user = User(wallet_address=request.wallet_address)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create new nonce
    nonce = create_nonce()
    user.nonce = nonce
    db.commit()
    
    return {
        "nonce": nonce,
        "message": "Please sign this message to verify your wallet ownership"
    }

@router.post("/verify", response_model=dict)
async def verify_signature(
    request: SignatureRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify wallet signature and return JWT token.
    """
    user = db.query(User).filter(User.wallet_address == request.wallet_address).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_wallet_ownership(
        request.wallet_address,
        request.signature,
        user.nonce
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Create access token
    access_token = create_access_token(subject=user.wallet_address)
    
    # Clear nonce after successful verification
    user.nonce = None
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserInDB)
async def get_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user