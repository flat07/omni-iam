# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()