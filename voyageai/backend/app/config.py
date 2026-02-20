from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = Field(default='development', alias='APP_ENV')
    app_name: str = Field(default='VoyageAI', alias='APP_NAME')
    app_version: str = Field(default='1.0.0', alias='APP_VERSION')
    api_prefix: str = Field(default='/api/v1', alias='API_PREFIX')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')

    database_url: str = Field(alias='DATABASE_URL')
    redis_url: str = Field(alias='REDIS_URL')

    vector_provider: str = Field(default='faiss', alias='VECTOR_PROVIDER')
    pinecone_api_key: str = Field(default='', alias='PINECONE_API_KEY')
    pinecone_index: str = Field(default='voyageai-index', alias='PINECONE_INDEX')
    pinecone_environment: str = Field(default='us-east-1', alias='PINECONE_ENVIRONMENT')

    rate_limit: str = Field(default='60/minute', alias='RATE_LIMIT')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
