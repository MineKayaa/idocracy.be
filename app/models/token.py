from pydantic import BaseModel, Field
from datetime import datetime


class TokenBase(BaseModel):
    user_id: str
    token: str
    expires_at: datetime


class TokenCreate(TokenBase):
    pass


class TokenInDB(TokenBase):
    id: str = Field(alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    }


class TokenResponse(TokenBase):
    id: str = Field(alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {}
    } 