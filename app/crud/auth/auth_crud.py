import os
from jose import ExpiredSignatureError, JWTError, jwt
from schema.token import TokenData
from sqlalchemy.orm import Session
from typing import Annotated
from crud.crud_role import get_role_by_uuid
from crud.crud_permission import get_permissions_for_menu, get_permissions_by_lang
from utils.hash import verify_str_hash
from crud.crud_user import get_user_by_email, get_profile_id_by_user_id
from utils.functions_jwt import validate_token, create_access_token, generate_new_tokens
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from utils.db import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY_TOKEN")
ALGORITHM = "HS256"

def validate_token(token_data: str = Depends(oauth2_scheme)):
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
        raise HTTPException(status_code=403, detail=str(ex))
    except JWTError as ex:
        print("-->JWTError")
        print(ex)
        raise credentials_exception

    return token_data
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return 2
    if not verify_str_hash(password, user.hashed_pass):
        return 3
    return user

def get_user(db, username: str):
    user = get_user_by_email(db, username)
    if not user:
        return None
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Los tokens de /refresh/token solo incluyen "user_email"
        username: str = payload.get("sub") or payload.get("user_email")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except JWTError:
        raise credentials_exception
    db = SessionLocal()
    try:
        user = get_user(db, username)
    finally:
        db.close()
    if user is None:
        raise credentials_exception
    return user


def get_permissions_menu(db, user, lang):
    # ADMIN
    if (
        user.is_admin == True
        and user.is_coordinator == True
        and user.is_employee == True
    ):
        permissions_list = get_permissions_by_lang(db, user.role_id, lang)
    # COORDINADOR
    elif (
        user.is_admin == False
        and user.is_coordinator == True
        and user.is_employee == True
    ):
        permissions_list = get_permissions_for_menu(
            db, user.role_id, False, True, True, lang
        )
    # STAFF EMPLEADO
    elif (
        user.is_admin == False
        and user.is_coordinator == False
        and user.is_employee == True
    ):
        permissions_list = get_permissions_for_menu(
            db, user.role_id, False, False, True, lang
        )
    # STAFF PROSPECTO
    elif (
        user.is_admin == False
        and user.is_coordinator == False
        and user.is_employee == False
    ):
        permissions_list = get_permissions_for_menu(
            db, user.role_id, False, False, False, lang
        )

    list_menu_permission = []
    
    print(permissions_list)

    for i in permissions_list:
        a = i.__dict__
        a.pop("id")
        a.pop("language")
        a.pop("is_coordinator")
        a.pop("is_admin")
        a.pop("is_employee")
        a.pop("target")
        a.pop("role_id")
        a.pop("is_active")
        a.pop("created_at")
        a.pop("updated_at")
        a.pop("_sa_instance_state")

        list_menu_permission.append(a)

    print(list_menu_permission)

    return list_menu_permission
