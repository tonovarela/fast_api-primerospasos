
import os
import jwt 
from jwt.exceptions import ExpiredSignatureError ,InvalidTokenError
from fastapi import Depends, HTTPException, status
from datetime import datetime ,timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
ALGORTHIM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES =int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 


def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc)+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(payload=to_encode,key= SECRET_KEY,algorithm=ALGORTHIM)    
    return token
    

def decode_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORTHIM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

async def get_currrent_user(token:str= Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)        
        if payload is None:
            raise credentials_exception
        email: str = payload.get("email")
        username: str = payload.get("username")
        if username is None:            
            raise credentials_exception
        return {"email": email, "username": username}
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:        
        print("Unexpected error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en el servidor",
            headers={"WWW-Authenticate": "Bearer"}
        )       
        
        

    
    

