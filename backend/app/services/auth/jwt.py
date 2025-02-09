from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.core import security

class JWTService:
    @staticmethod
    def create_access_token(
        subject: str,
        extra_data: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        return security.create_access_token(
            subject=subject,
            extra_data=extra_data,
            expires_delta=expires_delta
        )

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and verify JWT token"""
        return security.decode_jwt_token(token)

    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate JWT token"""
        try:
            security.decode_jwt_token(token)
            return True
        except:
            return False

jwt_service = JWTService()