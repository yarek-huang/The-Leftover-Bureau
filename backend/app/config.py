from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://app:app@db:5432/leftover"
    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "leftover"

    jwt_secret: str = "change-me"
    jwt_expires_days: int = 30

    llm_text_provider: str = "zhipu"
    llm_text_model: str = "glm-4.6-flash"
    llm_text_api_key: str = ""
    llm_vision_provider: str = "zhipu"
    llm_vision_model: str = "glm-4.6v-flash"
    llm_vision_api_key: str = ""

    enforce_https: bool = False
    password_strength_check: bool = False
    login_rate_limit: bool = False
    cors_origins: str = "*"


settings = Settings()
