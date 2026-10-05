from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "notification-service"
    database_url: str = "postgresql://orders:local-change-me@postgres:5432/orders"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "local-only-change-this"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    upstream_user: str = "http://user-service:8001"
    upstream_restaurant: str = "http://restaurant-service:8002"
    upstream_order: str = "http://order-service:8003"
    upstream_payment: str = "http://payment-service:8004"
    upstream_notification: str = "http://notification-service:8005"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
