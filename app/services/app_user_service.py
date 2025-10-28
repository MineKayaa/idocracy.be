from typing import List, Optional
from app.database import get_database
from app.models.app_user import AppUserCreate, AppUserUpdate, AppUserInDB, AppUserResponse
from app.models.user import UserResponse
from fastapi import HTTPException, status
from datetime import datetime
import uuid


class AppUserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.app_users

    async def add_user_to_app(self, app_user_data: AppUserCreate) -> AppUserResponse:
        # Check if user is already in the app
        existing = await self.collection.find_one({
            "user_id": app_user_data.user_id,
            "app_id": app_user_data.app_id
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in this app"
            )
        
        # Create app_user document with string ID
        app_user_dict = app_user_data.dict()
        app_user_dict["_id"] = str(uuid.uuid4())
        app_user_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(app_user_dict)
        
        # Get created app_user
        created_app_user = await self.collection.find_one({"_id": app_user_dict["_id"]})
        return AppUserResponse(**created_app_user)

    async def get_app_users(self, app_id: str) -> List[UserResponse]:
        try:
            # Get all app_user relationships for this app
            app_users = []
            cursor = self.collection.find({"app_id": app_id})
            async for app_user in cursor:
                app_users.append(AppUserResponse(**app_user))
            
            # Get user details for each app_user
            users = []
            for app_user in app_users:
                user = await self.db.users.find_one({"_id": app_user.user_id})
                if user:
                    users.append(UserResponse(**user))
            
            return users
        except Exception:
            return []

    async def remove_user_from_app(self, app_id: str, user_id: str) -> bool:
        try:
            result = await self.collection.delete_one({
                "app_id": app_id,
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception:
            return False

    async def update_user_roles(self, app_id: str, user_id: str, roles: List[str]) -> Optional[AppUserResponse]:
        try:
            result = await self.collection.update_one(
                {
                    "app_id": app_id,
                    "user_id": user_id
                },
                {"$set": {"roles": roles}}
            )
            
            if result.modified_count:
                updated_app_user = await self.collection.find_one({
                    "app_id": app_id,
                    "user_id": user_id
                })
                if updated_app_user:
                    return AppUserResponse(**updated_app_user)
            return None
        except Exception:
            return None

    async def get_user_apps(self, user_id: str) -> List[str]:
        """Get all app IDs that a user belongs to"""
        try:
            app_ids = []
            cursor = self.collection.find({"user_id": user_id})
            async for app_user in cursor:
                app_ids.append(app_user["app_id"])
            return app_ids
        except Exception:
            return [] 