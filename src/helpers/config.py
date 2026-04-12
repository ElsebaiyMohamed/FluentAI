from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FluentAI"
    APP_VERSION: str = "0.1"
    AUTHOR: str = "your name"
    FILE_ALLOWED_EXTENSIONS: list[str] = ["WAV", "MP3", "M4A"]
    MAX_FILE_SIZE_MB: int = 5
    FILE_DEFAULT_CHUNK_SIZE: int = 2048
    
    class Config:
        env_file = "src/.env"


def get_settings() -> Settings:
    return Settings() 