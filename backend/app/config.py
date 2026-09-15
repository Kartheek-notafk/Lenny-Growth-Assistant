from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lenny"

    llm_provider: str = "ollama"  # "ollama" or "openai"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    cors_origins: str = "http://localhost:5173"

    # Retrieval / conversation tuning
    retrieval_top_k: int = 5
    history_turns: int = 6  # number of prior user+assistant turns fed back as context

    # Resilience
    llm_timeout_seconds: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
