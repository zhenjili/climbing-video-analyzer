from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    max_video_size_mb: int = 100
    allowed_extensions: set[str] = {".mp4", ".mov", ".avi", ".mkv"}

    model_config = {"env_file": ".env"}


settings = Settings()
