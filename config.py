from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = None
    database_type: Optional[str] = None
    database_user: Optional[str] = None
    database_password: Optional[str] = None
    database_host: Optional[str] = None
    database_port: Optional[str] = None
    database_name: Optional[str] = None
    super_admin_name: Optional[str] = None
    super_admin_email: Optional[str] = None
    super_admin_password: Optional[str] = None
    deploy: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


SETTINGS = get_settings()
