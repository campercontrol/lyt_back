import os
from datetime import datetime, timedelta
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import jwt
from sqlalchemy.orm import Session

from crud.crud_user import get_user_by_email, get_profile_id_by_user_id
from crud.crud_role import get_role_by_uuid
from crud.crud_permission import get_permissions_for_menu, get_permissions_by_lang
from schema.token import Token, TokenRefresh, TokenCreate
from utils.db import SessionLocal
from utils.functions_jwt import validate_token, create_access_token, generate_new_tokens
from utils.hash import verify_str_hash

SECRET_KEY = "39d87423287d550c71e16d02fa7c4a522752a20bed9c505740b13aceeab5bf8a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 35))

token_routes = APIRouter()

# Dependency


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def authenticate_user(db, username: str, password: str):
    print("USERNAME")
    print(username)
    user = get_user_by_email(db, username)
    print("USER DB")
    print(user)

    if not user:
        return 2
    if not verify_str_hash(password, user.hashed_pass):
        return 3
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


@token_routes.post("/token", response_model=Token, tags=["Token"])
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: TokenCreate = Depends()
):
    """
    Status de login:
        - Si el detail es 1 el login fue exitoso, el usuario y contraseña son
          correctos.
        - Si el detail es 2 el login fue incorrecto, el usuario no existe
        - Si el detail es 3 el login fue incorrecto, la contraseña es inco-
          rrecta.
    """
    # print(form_data.username)
    user = authenticate_user(db, form_data.username, form_data.password)
    # print(user)
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    if user == 2:
        detail = 2
        return JSONResponse(content={"detail": detail}, headers={"WWW-Authenticate": "Bearer"})
    elif user == 3:
        detail = 3
        return JSONResponse(content={"detail": detail}, headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    role = get_role_by_uuid(db, user.role_id)

    # menu = get_permissions_menu(db, user, form_data.lang)

    profile_id = get_profile_id_by_user_id(db, user.id)

    access_token = create_access_token(
        data={
            "user_name": "",
            "user_email": user.email,
            "user_id": user.id,
            "user_active": user.is_active,
            "user_employee": user.is_employee,
            "user_coordinator": user.is_coordinator,
            "user_admin": user.is_admin,
            "role_name": role.name,
            "role_id": role.id,
            "profile_id": profile_id,
            "lang": form_data.lang,
            "access_token_expires": str(access_token_expires),
            "refresh_token_expires": str(refresh_token_expires),
        },
        expires_delta=access_token_expires,
    )
    refresh_token = create_access_token(
        data={
            "user_name": "",
            "user_email": user.email,
            "user_id": user.id,
            "user_active": user.is_active,
            "user_employee": user.is_employee,
            "user_coordinator": user.is_coordinator,
            "user_admin": user.is_admin,
            "role_name": role.name,
            "role_id": role.id,
            "profile_id": profile_id,
            "lang": form_data.lang,
            "access_token_expires": str(access_token_expires),
            "refresh_token_expires": str(refresh_token_expires),
        },
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "detail": 1,
    }


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