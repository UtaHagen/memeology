from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # Weaviate 配置
    WEAVIATE_URL: str
    WEAVIATE_API_KEY: str

    # Hugging Face 配置
    HUGGINGFACE_TOKEN: str

    # Modal 配置
    MODAL_TOKEN_ID: str
    MODAL_TOKEN_SECRET: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置"""
    return Settings()


settings = get_settings()
