from pydantic_settings import BaseSettings

from core.env_manager import EnvManager


class Config(BaseSettings):
    IMAGE_DIR: str = EnvManager.get("IMAGE_DIR", "images")
    VIDEO_DIR: str = EnvManager.get("VIDEO_DIR", "videos")
    AUDIO_DIR: str = EnvManager.get("AUDIO_DIR", "audios")
    DOCS_DIR: str = EnvManager.get("DOCS_DIR", "docs")

    IMAGE_SIZES: str = EnvManager.get("IMAGE_SIZES", "100x100,200x200,400x400")
    UPLOAD_DIR: str = EnvManager.get("UPLOAD_FOLDER", "uploads")

    BASE_FILE_URL: str = EnvManager.get("BASE_FILE_URL", "http://localhost:8000")


archive_setting = Config()
