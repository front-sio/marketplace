from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Define your secret key and algorithm
SECRET_KEY = "x=nm*-x5$b!1olbh71g3yo19w2#=pn8pz(jm1fe5yu=3+7e^^-"
ALGORITHM = "HS256"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
