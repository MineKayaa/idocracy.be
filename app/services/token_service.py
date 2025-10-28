from typing import Optional
from datetime import datetime, timedelta
from app.database import get_database
from app.models.token import TokenCreate, TokenInDB
from app.config import settings
import uuid


class TokenService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.tokens

    async def create_refresh_token(self, user_id: str, token: str) -> TokenInDB:
        # Set expiration
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        # Create token document with string ID
        token_dict = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at
        }
        
        result = await self.collection.insert_one(token_dict)
        
        # Get created token
        created_token = await self.collection.find_one({"_id": token_dict["_id"]})
        return TokenInDB(**created_token)

    async def get_refresh_token(self, token: str) -> Optional[TokenInDB]:
        token_doc = await self.collection.find_one({"token": token})
        if token_doc:
            return TokenInDB(**token_doc)
        return None

    async def delete_refresh_token(self, token: str) -> bool:
        try:
            result = await self.collection.delete_one({"token": token})
            return result.deleted_count > 0
        except Exception:
            return False

    async def delete_user_tokens(self, user_id: str) -> bool:
        """Delete all refresh tokens for a user (logout)"""
        try:
            result = await self.collection.delete_many({"user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database"""
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            return result.deleted_count
        except Exception:
            return 0 