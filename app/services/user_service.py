from typing import List, Optional
from app.database import get_database
from app.models.user import UserCreate, UserUpdate, UserInDB, UserResponse
from app.utils.auth import get_password_hash, verify_password
from fastapi import HTTPException, status
from datetime import datetime
import uuid


class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Check if user already exists
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user document with string ID
        user_dict = user_data.dict()
        user_dict["_id"] = str(uuid.uuid4())
        user_dict["password_hash"] = get_password_hash(user_data.password)
        user_dict["created_at"] = datetime.utcnow()
        del user_dict["password"]
        
        result = await self.collection.insert_one(user_dict)
        
        # Get created user
        created_user = await self.collection.find_one({"_id": user_dict["_id"]})
        return UserResponse(**created_user)

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        try:
            user = await self.collection.find_one({"_id": user_id})
            if user:
                return UserResponse(**user)
            return None
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user = await self.collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def get_all_users(self) -> List[UserResponse]:
        users = []
        cursor = self.collection.find({})
        async for user in cursor:
            users.append(UserResponse(**user))
        return users

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        try:
            update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_user_by_id(user_id)
            
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_user_by_id(user_id)
            return None
        except Exception:
            return None

    async def delete_user(self, user_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user 