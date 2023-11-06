from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    cloud_api_key: str
    cloud_api_secret: str
    cloud_api_name: str

    class Config:
        env_file = ".env_prod"

settings = Settings()