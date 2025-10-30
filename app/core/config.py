import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://pets_user:pets_password@localhost:5432/pets_db"
    )
    
    class Config:
        env_file = ".env"


settings = Settings()