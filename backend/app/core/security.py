from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from eth_account.messages import encode_defunct
from web3 import Web3
from app.core.config import settings

ALGORITHM = "HS256"

def create_nonce() -> str:
    """
    Creates a unique nonce for wallet signature.
    """
    return f"Welcome to SYNTHR! Please sign this message to verify your wallet. Nonce: {datetime.utcnow().timestamp()}"

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Creates a JWT token for the user.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

def verify_signature(wallet_address: str, message: str, signature: str) -> bool:
    """
    Verifies an Ethereum wallet signature.
    """
    try:
        w3 = Web3()
        message_hash = encode_defunct(text=message)
        recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

def verify_wallet_ownership(wallet_address: str, signature: str, nonce: str) -> bool:
    """
    Verifies wallet ownership through signature.
    """
    return verify_signature(wallet_address, nonce, signature)