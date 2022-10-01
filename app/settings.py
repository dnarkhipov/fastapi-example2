import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn

logger = logging.getLogger("app")


class PostgresDsnV2(PostgresDsn):
    def __repr__(self) -> str:
        return f"{self.scheme}://{self.user}:{self.password}@{self.host}{self.path}"

    def __str__(self) -> str:
        return f"{self.scheme}://{self.user}:********@{self.host}{self.path}"


class Settings(BaseSettings):
    TZ: str = "Europe/Moscow"
    TESTING: bool = False
    DEBUG: bool = False
    DB_SQL_ECHO: bool = False
    API_PREFIX: str = "/v1"
    DB_DSN: Optional[PostgresDsnV2] = None
    DB_TEST_DSN: Optional[PostgresDsnV2] = None

    # backend_cors_origins is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Used only in DEBUG-mode. Proxy-server prefix passed to OpenAPI client, must be "" if no proxy.
    PROXY_PREFIX: str = "/accounts"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    logger.debug("Loading config settings from the environment ...")
    return Settings()


app_settings = get_settings()
