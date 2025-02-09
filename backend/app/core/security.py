from datetime import datetime, timedelta
from typing import Any, Union, Dict
from jose import jwt
from eth_account.messages import encode_defunct
from web3 import Web3
from app.core.config import settings

ALGORITHM = "HS256"

# JWT Functions
def create_access_token(
    subject: Union[str, Any],
    extra_data: Dict[str, Any] = None,
    expires_delta: timedelta = None
) -> str:
    """Creates a JWT token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    if extra_data:
        to_encode.update(extra_data)
        
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """Decodes and validates a JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

# Wallet Functions
def verify_eth_signature(wallet_address: str, message: str, signature: str) -> bool:
    """Verifies an Ethereum signature."""
    try:
        w3 = Web3()
        message_hash = encode_defunct(text=message)
        recovered_address = w3.eth.account.recover_message(
            message_hash, 
            signature=signature
        )
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

def is_valid_eth_address(address: str) -> bool:
    """Validates Ethereum address format."""
    w3 = Web3()
    return w3.is_address(address)

def get_checksum_address(address: str) -> str:
    """Converts address to checksum format."""
    w3 = Web3()
    return w3.to_checksum_address(address)

# Nonce Generation
def generate_auth_message(nonce: str) -> str:
    """Generates standardized authentication message."""
    timestamp = datetime.utcnow().isoformat()
    return (
        f"Welcome to SYNTHR!\n\n"
        f"Please sign this message to verify your wallet.\n\n"
        f"Nonce: {nonce}\n"
        f"Timestamp: {timestamp}"
    )