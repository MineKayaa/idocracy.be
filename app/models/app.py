from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AppBase(BaseModel):
    name: str
    redirect_uris: List[str] = []
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class AppCreate(AppBase):
    pass


class AppUpdate(BaseModel):
    name: Optional[str] = None
    redirect_uris: Optional[List[str]] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class AppInDB(AppBase):
    id: str = Field(alias="_id")
    client_id: str
    client_secret: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    }


class AppResponse(AppBase):
    id: str = Field(alias="_id")
    client_id: str
    client_secret: str
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    } 