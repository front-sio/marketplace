from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.core.config import settings
from fastapi import Depends, HTTPException
from app.models import User
from app.core.token import verify_token
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt








oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode and verify the token, then extract the user
        payload = verify_token(token)
        user = await User.get(email=payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return user


