import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgres://user:password@localhost:5432/marketplace")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "x=nm*-x5$b!1olbh71g3yo19w2#=pn8pz(jm1fe5yu=3+7e^^-")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "x=nm*-x5$b!1olbh71g3yo19w2#=pn8pz(jm1fe5yu=3+7e^^-")  # Set your secret key here
    JWT_ALGORITHM: str = "HS256"  # Algorithm used for signing the JWT
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time in minutes


    class Config:
        env_file = ".env"

settings = Settings()