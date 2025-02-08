from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_jwt_token
from app.services.auth.wallet import verify_wallet_signature

security = HTTPBearer()

def get_db() -> Generator:
    """
    Database dependency to be used in routes.
    Creates a new database session for each request and closes it afterwards.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
async def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_jwt_token(token.credentials)
        wallet_address: str = payload.get("sub")
        if wallet_address is None:
            raise credentials_exception
        
        # Getting user from DB
        user = db.query(User).filter(User.wallet_address == wallet_address).first()
        if user is None:
            raise credentials_exception
            
        return user
    except:
        raise credentials_exception
    
async def get_current_active_user(
    current_user = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure the user is active.
    Can be extended to check for banned/inactive users.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user