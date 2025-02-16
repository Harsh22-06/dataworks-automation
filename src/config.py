from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Set

class SecuritySettings(BaseSettings):
    allowed_paths: Set[str] = {"/data"}
    restricted_operations: Set[str] = {"delete", "remove", "rm", "rmdir", "unlink"}
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: Set[str] = {".txt", ".md", ".json", ".csv", ".db", ".mp3", ".png", ".jpg"}

class Settings(BaseSettings):
    data_dir: str = "/data"
    aiproxy_token: str
    model_name: str = "gpt-4-mini"
    max_tokens: int = 150
    temperature: float = 0
    debug: bool = False
    security: SecuritySettings = SecuritySettings()

    class Config:
        env_file = ".env"

settings = Settings()