from typing import List, Optional
from app.database import get_database
from app.models.app import AppCreate, AppUpdate, AppInDB, AppResponse
from app.utils.auth import generate_client_id, generate_client_secret, get_password_hash
from fastapi import HTTPException, status
from datetime import datetime
import uuid

class AppService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.apps

    async def create_app(self, app_data: AppCreate, created_by: str) -> AppResponse:
        # Generate client credentials
        client_id = generate_client_id()
        client_secret = generate_client_secret()
        client_secret_hash = get_password_hash(client_secret)
        
        # Create app document with string ID
        app_dict = app_data.dict()
        app_dict["_id"] = str(uuid.uuid4())
        app_dict["client_id"] = client_id
        app_dict["client_secret"] = client_secret_hash
        app_dict["created_by"] = created_by
        app_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(app_dict)
        
        # Get created app
        created_app = await self.collection.find_one({"_id": app_dict["_id"]})
        app_response = AppResponse(**created_app)
        
        # Return with plain client_secret for initial creation
        app_response.client_secret = client_secret
        return app_response

    async def get_app_by_id(self, app_id: str) -> Optional[AppResponse]:
        try:
            app = await self.collection.find_one({"_id": app_id})
            if app:
                return AppResponse(**app)
            return None
        except Exception:
            return None

    async def get_all_apps(self) -> List[AppResponse]:
        apps = []
        cursor = self.collection.find({})
        async for app in cursor:
            apps.append(AppResponse(**app))
        return apps

    async def update_app(self, app_id: str, app_data: AppUpdate) -> Optional[AppResponse]:
        try:
            update_data = {k: v for k, v in app_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_app_by_id(app_id)
            
            result = await self.collection.update_one(
                {"_id": app_id},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_app_by_id(app_id)
            return None
        except Exception:
            return None

    async def delete_app(self, app_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": app_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def verify_client_credentials(self, client_id: str, client_secret: str) -> Optional[AppInDB]:
        app = await self.collection.find_one({"client_id": client_id})
        if not app:
            return None
        
        app_in_db = AppInDB(**app)
        # Verify client secret hash
        from app.utils.auth import verify_password
        if not verify_password(client_secret, app_in_db.client_secret):
            return None
        
        return app_in_db 