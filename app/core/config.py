import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgres://user:password@localhost:5432/marketplace",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # JWT Configuration
    SECRET_KEY: str = Field(
        default="x=nm*-x5$b!1olbh71g3yo19w2#=pn8pz(jm1fe5yu=3+7e^^-", 
        env="SECRET_KEY",
        description="Secret key for signing JWT tokens"
    )
    ALGORITHM: str = Field(
        default="HS256", 
        env="ALGORITHM",
        description="Algorithm used for JWT signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Expiration time of JWT tokens in minutes"
    )

    class Config:
        env_file = ".env"  # Load environment variables from the .env file

# Initialize settings
settings = Settings()
