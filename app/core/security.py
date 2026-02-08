
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

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

error_500_exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
        headers={"WWW-Authenticate": "Bearer"},
    )   
    
     

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
    
    try:
        payload = decode_token(token)        
        if payload is None:
            raise credentials_exception
        email: str = payload.get("email")
        username: str = payload.get("username")
        if username is None:            
            raise credentials_exception
        return {"email": email, "username": username, "full_name": payload.get("full_name")}
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exception
    except Exception as e:        
        print("Unexpected error:", str(e))
        raise error_500_exception  
        
        

    
    

