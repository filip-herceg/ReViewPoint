from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    env: str = "dev"
    db_url: str = ...
    openai_api_key: str = ...

    model_config = ConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
