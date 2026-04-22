from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = "fastapi"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "neurorx"
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 14

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
