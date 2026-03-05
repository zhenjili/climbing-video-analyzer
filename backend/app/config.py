from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: Path = Path("data/uploads")
    output_dir: Path = Path("data/outputs")
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    max_video_size_mb: int = 100
    allowed_extensions: set[str] = {".mp4", ".mov", ".avi", ".mkv"}
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    model_config = {"env_file": ".env"}


settings = Settings()
