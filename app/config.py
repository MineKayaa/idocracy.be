from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "idocracy"
    
    # JWT
    secret_key: str = "u5qjPZJ+9tAjjGv5h9sUCBekHY7V4TnlfyPuAnRUl6I="
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # App
    debug: bool = True
    api_v1_str: str = "/api/v1"
    project_name: str = "IDocracy API"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 