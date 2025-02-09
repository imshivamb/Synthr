from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.services.auth.jwt import jwt_service
from app.services.auth.wallet import wallet_service
from app.crud.user import user as user_crud
from app.schemas.auth import Token

class AuthService:
    """
    High-level authentication service that combines JWT and wallet authentication.
    This service will be used directly by API routes.
    """
    
    async def init_wallet_auth(
        self,
        db: Session,
        wallet_address: str
    ) -> Tuple[str, str]:
        """
        Initialize wallet authentication process by generating nonce
        """
        # Validate wallet address
        if not wallet_service.is_valid_address(wallet_address):
            raise ValueError("Invalid wallet address")

        # Convert to checksum address
        wallet_address = wallet_service.checksum_address(wallet_address)

        # Create or get user
        user = await user_crud.get_by_wallet(db, wallet_address=wallet_address)
        if not user:
            user = await user_crud.create_with_wallet(db, wallet_address=wallet_address)

        # Generate new nonce and message
        nonce, message = wallet_service.create_nonce()

        # Save nonce to user
        await user_crud.update_nonce(db, user_id=user.id, nonce=nonce)

        return nonce, message

    async def verify_wallet_auth(
        self,
        db: Session,
        wallet_address: str,
        signature: str,
        nonce: str
    ) -> Optional[Token]:
        """
        Verify wallet signature and generate access token
        """
        # Validate wallet address
        if not wallet_service.is_valid_address(wallet_address):
            return None

        # Convert to checksum address
        wallet_address = wallet_service.checksum_address(wallet_address)

        # Get user
        user = await user_crud.get_by_wallet(db, wallet_address=wallet_address)
        if not user or user.nonce != nonce:
            return None

        # Verify signature using stored nonce
        message = wallet_service.create_auth_message(nonce)
        if not wallet_service.verify_signature(message, signature, wallet_address):
            return None

        # Clear nonce after successful verification
        await user_crud.update_nonce(db, user_id=user.id, nonce=None)

        # Generate access token
        access_token = jwt_service.create_access_token(
            subject=wallet_address,
            extra_data={
                "user_id": user.id,
                "type": "wallet"
            }
        )

        return Token(
            access_token=access_token,
            token_type="bearer"
        )

    async def get_current_user_id(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token
        """
        try:
            decoded = jwt_service.decode_token(token)
            return decoded.get("user_id")
        except:
            return None

    async def get_current_wallet(self, token: str) -> Optional[str]:
        """
        Extract wallet address from JWT token
        """
        try:
            decoded = jwt_service.decode_token(token)
            return decoded.get("sub")
        except:
            return None

    async def validate_token(self, token: str) -> bool:
        """
        Validate JWT token
        """
        return jwt_service.validate_token(token)

auth_service = AuthService()