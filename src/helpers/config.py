from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):

    MONGODB_URL: str
    MONGODB_DATABASE: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"

def get_settings() -> Settings:
    return Settings()
