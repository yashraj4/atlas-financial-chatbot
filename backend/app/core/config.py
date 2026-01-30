
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Atlas Financial Assistant"
    API_V1_STR: str = "/api/v1"
    
    # LLM Keys
    GOOGLE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None
    
    # Database
    # Defaulting to a local docker URL
    DATABASE_URL: str = "postgresql://postgres:postgrespassword@localhost:5432/barclays_genai"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
