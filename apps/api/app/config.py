# ════════════════════════════════════════════════════════════
# FastAPI Application Configuration
# ════════════════════════════════════════════════════════════

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "SkillMaster AI API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:4000",
    ]

    # Database
    database_url: str = "sqlite+aiosqlite:///./skillmaster.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"

    # Auth
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # AI Services
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_ai_api_key: str = ""

    # Blockchain (Polygon Mumbai testnet)
    blockchain_rpc_url: str = ""
    blockchain_private_key: str = ""
    blockchain_contract_address: str = ""

    # WebSocket
    ws_heartbeat_interval: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    return Settings()
