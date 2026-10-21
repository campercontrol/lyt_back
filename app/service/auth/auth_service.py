import os
from typing import Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from schema.token import Token, TokenRefresh, TokenCreate
from sqlalchemy.orm import Session
from utils.db import SessionLocal
from typing import Annotated, Optional
from crud.auth.auth_crud import (
    authenticate_user,
    get_role_by_uuid,
    get_profile_id_by_user_id,
    validate_token,
    create_access_token,
    generate_new_tokens,
    get_permissions_menu,
)

SECRET_KEY = os.getenv("SECRET_KEY_TOKEN")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 35))

token_routes = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@token_routes.post("/token", tags=["Token"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user == 2:
        raise HTTPException(
            status_code=401,
            detail={"status": 2, "msg": "El usuario no existe"},
            headers={"WWW-Authenticate": "Bearer"})

    elif user == 3:
        raise HTTPException(
            status_code=401,
            detail={"status": 3, "msg": "La contraseña es incorrecta"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)


    role = get_role_by_uuid(db, user.role_id)

    profile_id = get_profile_id_by_user_id(db, user.id)

    access_token = create_access_token(data={
            "user_name": "",
            "sub": user.email ,
            "user_email": user.email,
            "user_id": user.id,
            "user_active": user.is_active,
            "user_employee": user.is_employee,
            "user_coordinator": user.is_coordinator,
            "user_admin": user.is_admin,
            "role_name": role.name,
            "role_id": role.id,
            "profile_id": profile_id,
            # "lang": form_data.lang,
            "access_token_expires": str(access_token_expires),
            "refresh_token_expires": str(refresh_token_expires),
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")




@token_routes.post("/refresh/token", tags=["Token"])
async def refresh_access_token(
    token_refresh_data: TokenRefresh,
    db: Session = Depends(get_db),
    response: Response = 200,
):
    status_token, respuesta = validate_token(token_refresh_data.access_token)
    # print(">>>>>>>>>>>")
    # print(status_token)
    # print(respuesta)
    # print(">>>>>>>>>>>")

    if status_token == 403:
        # realiza Verificacion del token Refresh
        response.status_code = 403
        status_token, respuesta = validate_token(token_refresh_data.refresh_token)
        if status_token == 403:
            response.status_code = 401
            respuesta = {
                "mensaje": "Ambos tokens estan expirados, no se puede refrescar",
                "data": [],
            }
        elif status_token == 200:
            response.status_code = 200
            respuesta = generate_new_tokens(db, respuesta.username)
        else:
            response.status_code = 401
    elif status_token == 200:
        # print(respuesta.username)
        respuesta = generate_new_tokens(db, respuesta.username)
    else:
        response.status_code = 401

    return respuesta
