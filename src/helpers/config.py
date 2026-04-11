from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    AUTHOR: str
    FILE_ALLOWED_EXTENSIONS: list[str]   
    MAX_FILE_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    class Config:
        env_file = "src/.env"


def get_settings() -> Settings:
    return Settings() 