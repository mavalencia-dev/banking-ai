from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Banking AI"

    app_version: str = "0.1.0"

    ollama_host: str = "http://localhost:11434"

    ollama_model: str = "llama3.2"

    database_url: str = (
        "postgresql+psycopg://"
        "banking:banking@localhost:5432/banking"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()