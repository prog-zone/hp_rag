from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, values: any) -> any:
        if isinstance(v, str) and v:
            return v
        return f"postgresql://{values.data['POSTGRES_USER']}:{values.data['POSTGRES_PASSWORD']}@{values.data['POSTGRES_SERVER']}:{values.data['POSTGRES_PORT']}/{values.data['POSTGRES_DB']}"

    DEBUG: bool = False
    OPENAI_API_KEY: str
    QDRANT_HOST: str = "localhost"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()