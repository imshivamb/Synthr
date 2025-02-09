import secrets
from typing import Tuple
from datetime import datetime

from app.core import security

class WalletService:
    def create_nonce(self) -> Tuple[str, str]:
        """Create a new nonce and message for wallet signing"""
        nonce = secrets.token_hex(32)
        message = security.generate_auth_message(nonce)
        return nonce, message

    def verify_signature(
        self,
        message: str,
        signature: str,
        wallet_address: str
    ) -> bool:
        """Verify an Ethereum signature"""
        return security.verify_eth_signature(
            wallet_address=wallet_address,
            message=message,
            signature=signature
        )

    def is_valid_address(self, address: str) -> bool:
        """Check if a string is a valid Ethereum address"""
        return security.is_valid_eth_address(address)

    def checksum_address(self, address: str) -> str:
        """Convert address to checksum format"""
        return security.get_checksum_address(address)

    def create_auth_message(self, nonce: str) -> str:
        """Create a standard authentication message"""
        return security.generate_auth_message(nonce)

wallet_service = WalletService()