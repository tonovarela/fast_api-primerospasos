from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import  OAuth2PasswordRequestForm
from app.core.security import create_access_token,get_currrent_user
from datetime import timedelta
from .schema import UserPublic
FAKE_USERS ={
    "ricardo":{ "username":"ricardo", "full_name":"Ricardo Lopes", "email":"ricardo@live.com","password":"12345"},
    "alumno":{ "username":"alumno", "full_name":"Alumno Test", "email":"alumno@live.com","password":"123456"},
    "tonovarela":{ "username":"tonovarela", "full_name":"Antonio Varela", "email":"tonovarela@live.com","password":"12345"}
}


from .schema import Token
router= APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username) 
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")    
    token = create_access_token(data={"full_name": user["full_name"],"username": user["username"],"email": user["email"]},expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me",response_model=UserPublic)
async def read_me(current_user: UserPublic = Depends(get_currrent_user)):
    return {"email": current_user["email"], "username": current_user["username"]}

    
