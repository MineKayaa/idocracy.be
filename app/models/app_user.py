from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AppUserBase(BaseModel):
    user_id: str
    app_id: str
    roles: List[str] = ["viewer"]


class AppUserCreate(AppUserBase):
    pass


class AppUserUpdate(BaseModel):
    roles: Optional[List[str]] = None


class AppUserInDB(AppUserBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    }


class AppUserResponse(AppUserBase):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    } 