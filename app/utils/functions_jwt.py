import os
from typing import Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from crud.crud_user import get_user_by_email
from model.user import User
from utils.db import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY_TOKEN")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 35))
ACCESS_RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 60
VERIFICATION_URL_EXPIRE_MINUTES = 21600
USER_VERIFY_URL_EXPIRE_MINUTES = 21600

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


#Validar token 
class TokenData(BaseModel):
    username: Union[str, None] = None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # print(">>>>>>")
    # print(token)
    # print(type(token))
    # print(">>>>>>")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user_email", "")
        print(f"username:{username}")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except ExpiredSignatureError as ex:
        print("-->ExpiredSignatureError")
        print(ex)
        expired_exception = HTTPException(
            status_code=403,
            detail=str(ex),
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise expired_exception
    except JWTError as ex:
        print("-->1")
        print(ex)
        raise credentials_exception
    user = get_user_by_email(db, token_data.username)
    # print(token_data.username)
    if user is None:
        print("-->2")
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # print(f"Current User : {current_user.__dict__}")
    return current_user


def validate_token(token_data):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token_data, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user_email", "")
        # print(f"validate_token-username:{username}")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError as ex:
        print("-->ExpiredSignatureError")
        print(ex)
        expired_exception = HTTPException(status_code=403, detail=str(ex))
        return 403, expired_exception
    except JWTError as ex:
        print("-->JWTError")
        print(ex)
        return 401, credentials_exception

    return 200, token_data


def validate_token_general(token_data):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        data = jwt.decode(token_data, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as ex:
        print("-->ExpiredSignatureError")
        print(ex)
        expired_exception = HTTPException(status_code=403, detail=str(ex))
        return 403, expired_exception
    except JWTError as ex:
        print("-->JWTError")
        print(ex)
        return 401, credentials_exception

    return 200, data


#Crear token 

# def create_user_verify_url(data: dict):
#     user_verify_url_expire = timedelta(minutes=USER_VERIFY_URL_EXPIRE_MINUTES)
#     token = create_access_token(data, expires_delta=user_verify_url_expire)
#     url = f'http://migracion.campercontrol.com/user/verify?t={token}' 
#     return url
    

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_new_tokens(db, user):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    #user_obj = get_user_by_email(db, user)

    #path_menu_permissions = get_permissions_menu(db, user_obj)

    access_token = create_access_token(
        data={"user_email": user},
        expires_delta=access_token_expires,
    )
    refresh_token = create_access_token(
        data={"user_email": user},
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def generate_access_token_reset_pass(email):
    access_token_expires = timedelta(minutes=ACCESS_RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"email": email},
        expires_delta=access_token_expires,
    )

    return access_token

def create_user_verification_url(data: dict):    
    base_url = os.getenv("FRONTEND_DEV_URL")
    
    access_token_expires = timedelta(minutes=VERIFICATION_URL_EXPIRE_MINUTES)
    
    token = create_access_token(data, access_token_expires)
    verification_url = f"{base_url}/verify?t={token}"
    
    return verification_url