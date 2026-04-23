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

    # Список разрешенных адресов фронтенда
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # VAPID ключи для Web Push Notifications (Добавь их в .env файл позже)
    VAPID_PUBLIC_KEY: str = "BEQjZp8pGErwoMDlal9izH0G_HDsTOIYbuLTIv7LRFyFt0UbOz9VtWkcOb1gPevShTAzpC2Vh7fSYHsgcRmMidY"
    VAPID_PRIVATE_KEY: str = "Fe0GHcQv4oPYcGkb5l3aKG1fdg3RNYb1NrhWGyuYkg0"
    VAPID_SUBJECT: str = "mailto:admin@neurorx.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
