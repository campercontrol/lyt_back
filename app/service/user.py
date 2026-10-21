from xmlrpc.client import boolean
import os
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from utils.hash import hash_str
from typing import Annotated, Optional
from schema.pagination.pagination_schema import Pagination
from helper.pagination_helpers import pagination_params
from crud.crud_user import (
    get_all_user,
    search_all_user,
    create_new_user,
    create_new_user_admin,
    get_user_by_uuid,
    get_users_all_info,
    get_user_by_email,
    crud_update_user_by_email,
    search_user_by_email,
    update_user_by_id,
    delete_user_by_id,
    get_user_info_by_email,
    get_user_delete_info
)
from crud.camps.season_crud import get_current_Season
from crud.catalogs.vaccine_crud import get_all_vaccine
from crud.catalogs.food_restriction_crud import get_all_food_restriction
from schema.user import UserCreate, UserModify, UserResetPassword, UserChangePassword, UserChangeEmail, UserSendMailResetPassword, UserCreateAdmin
from model.staffs import Staff, StaffRecord
from model.user import User
from model.medical.doctor import Doctor
from model.campers.parent import Parent
from model.campers.school import School
from model.staffs.staff_food_restriction import StaffFoodRestriction
from model.staffs.staff_vaccine import StaffVaccine
# from utils.check_role import chek_permission
from utils.db import SessionLocal
from utils.email_tools import send_simple_message
from helper.mailing_helpers import send_mail_template
from utils.functions_jwt import generate_access_token_reset_pass, validate_token_general
from utils.hash import hash_str
from utils.image_tools import write_image

# from utils.functions_jwt import get_current_active_user

ROLE_PARENT_ID = int(os.getenv("ROLE_PARENT_ID"))
ROLE_STAFF_ID = int(os.getenv("ROLE_STAFF_ID"))
ROLE_SCHOOL_ID = int(os.getenv("ROLE_SCHOOL_ID"))
ROLE_DOCTOR_ID = int(os.getenv("ROLE_DOCTOR_ID"))



user_routes = APIRouter()
# Endpoints sin autenticacion (recuperacion y cambio de cuenta con token propio)
user_public_routes = APIRouter()

# Dependency


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@user_routes.get("/usuario", tags=["Usuarios"])
def get_users(pagination: Annotated[Pagination, Depends(pagination_params)], is_active: boolean = True, db: Session = Depends(get_db)):
    NAME = "get_users"

    list_user = get_all_user(db, is_active, pagination)

    return {"data": list_user}

@user_routes.get("/search_usuario", tags=["Usuarios"])
def get_users(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db), is_active: boolean = True, email: Optional[str] = ''):
    NAME = "get_users"

    list_user = search_all_user(db, is_active, pagination, email)

    return {"data": list_user}
@user_routes.get("/usuario/info", tags=["Usuarios"])
def get_user_info(user_id: int, db: Session = Depends(get_db)):

    response = get_users_all_info(db, user_id)

    return response
@user_routes.get("/user_delete_info", tags=["Usuarios"])
def get_user_info_to_delete(user_id:str, db: Session = Depends(get_db)):
    response = get_user_delete_info(db, user_id)
    if response == None:
        raise HTTPException(status_code=404, detail="User not found")
    return response


@user_routes.post("/usuario", tags=["Usuarios"], status_code=200)
def create_user(user: UserCreateAdmin, response: Response, db: Session = Depends(get_db)):

    check_email = get_user_by_email(db, user.email)

    if check_email:
        return {"detail": {"status": 2, "msg": "Ya existe un usuario con ese correo"}}

    try:
        new_user = create_new_user_admin(db, user)
        new_user_role = new_user.role_id

        if new_user_role == ROLE_DOCTOR_ID:
            new_doctor = Doctor(
                name = "Default doctor name",
                lastname_father =  "Default doctor name",
                lastname_mother = "Default doctor",
                cellphone = "5555555555",
                login_id = new_user.id,
            )
            db.add(new_doctor)

        if new_user_role == ROLE_STAFF_ID:
            current_season = get_current_Season(db)
            catalog_vaccines = get_all_vaccine(db)
            catalog_food_restrictions = get_all_food_restriction(db)
            staff_new_record = None
            default_prospect_profile = None

            staff_new_record = StaffRecord(
                attend = 0,
                attended = 0,
                total = 0
            )
            db.add(staff_new_record)
            db.flush()

            default_prospect_profile = Staff(
                name = "Default staff name",
                lastname_father = "default",
                lastname_mother = "user",
                photo = "media/tmp/default_user.png",
                birthday = "2000-01-01",
                curp = "CURP",
                bio = "",
                facebook = "default staff",
                home_phone = "5555555555",
                cellphone = "5555555555",
                cv = "media/cv/default.pdf",
                gender_id = 4,
                record_id = staff_new_record.id,
                season_id = current_season["id"],
                login_id = new_user.id,
                coordinator = new_user.is_coordinator,
                employee_email_send = False,
                employee = new_user.is_employee
            )
            
            db.add(default_prospect_profile)
            db.flush()
            
            for vaccine in catalog_vaccines:
                staff_vaccine = StaffVaccine(
                    staff_id = default_prospect_profile.id,
                    vaccine_id = vaccine.id,
                    is_active = False
                     
                )
                db.add(staff_vaccine)
            db.flush()
            for food_restriction in catalog_food_restrictions:
                staff_food_restriction = StaffFoodRestriction(
                    staff_id = default_prospect_profile.id,
                    food_restriction_id = food_restriction.id,
                    is_active=False
                )
                db.add(staff_food_restriction)
            db.flush()
            
            db.commit()
                
        if new_user_role == ROLE_PARENT_ID:
            new_parent = Parent(
                tutor_name = "Default parent name",
                tutor_lastname_father = "Default parent name",
                toku_id= None,
                user_id = new_user.id,
                tutor_cellphone = "5555555555",
                tutor_home_phone = "5555555555",
                tutor_work_phone = "5555555555",
                contact_name = "Default contact name",
                contact_lastname_father = "Default contact name",
                contact_lastname_mother = "Default contact name",
                contact_cellphone = "5555555555",
                contact_home_phone = "5555555555",
                contact_work_phone = "5555555555",
                contact_email = "defaultparent@email.com"
            )
            db.add(new_parent)

        if new_user_role == ROLE_SCHOOL_ID:
            new_school = School(
                login_id = new_user.id,
                name = "Default school name",
                address = "Default school address",
                url = "wwww.default-school.com",
                contact = "Default school contact",
                phone = "555555555",
                cellphone = "555555555",
                email = "defaultschool@email.com",
                contact_second_name = "Default school contact",
                contact_second_phone = "Default school contact",
                contact_second_cellphone = "Default school contact",
                contact_second_email = "defaultschool@email.com",
                contact_third_name = "Default school contact",
                contact_third_phone = "Default school contact",
                contact_third_cellphone = "Default school contact",
                contact_third_email = "Default school contact",
                verify = True,
                active = True
            )
            db.add(new_school)
        db.commit()
        return {"detail": {"status": 1, "msg": "El usuario se creo correctamente"}}
    except Exception as ex:
        db.rollback()
        print(ex)
        return {"detail": {"status": 3, "msg": "Ocurrió un error al crear el usuario"}}


@user_routes.get("/usuario/{user_id}", tags=["Usuarios"])
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
):
    NAME = "get_user_by_id"

    resultado = get_user_by_uuid(db, user_id)
    return {"data": resultado}


@user_routes.patch("/usuario/{user_id}", tags=["Usuarios"])
def update_user(
    user_id: str,
    user: UserModify,
    response: Response,
    db: Session = Depends(get_db)
):
    response = update_user_by_id(db, user_id, user.dict())
    # if response == None:
    #     raise HTTPException(status_code=404, detail="User not found")
    if response['status'] == 3:
        raise HTTPException(status_code=500, detail=response)
    return {"detail": response}


# @user_routes.patch("/usuario/{user_id}", tags=["Usuarios"])
# def update_user(
#     user_id: str,
#     user: UserModify,
#     response: Response,
#     db: Session = Depends(get_db),
# ):
#     response = update_user_by_id(db, user_id, user)



#     # NAME = "update_user"

#     update_data = user.dict(exclude_unset=True)
#     print(update_data)
#     exist_user = get_user_by_uuid(db, user_id)
#     if not exist_user:
#         response.status_code = 401
#         return {"mensaje": "El usuario buscado no existe"}

#     if "passw" in update_data:
#         update_data["hashed_pass"] = hash_str(update_data["passw"])
#         update_data.pop("passw")

#     respuesta_update_user = crud_update_user_by_uuid(db, user_id, update_data)

#     if respuesta_update_user != 0:
#         exist_user = get_user_by_uuid(db, user_id)
#         return {"mensaje": "Actualizado Correctamente", "data": exist_user}
#     else:
#         return {"mensaje": "Ningun registro fue afectado", "data": ""}


@user_public_routes.post("/user/send_mail_password_reset", tags=["Usuarios"])
def reset_password(
    user_reset: UserSendMailResetPassword, response: Response, db: Session = Depends(get_db)
):

    user = get_user_by_email(db, user_reset.email)
    template_id = 2 # Password Recover
    if not user:
        # response.status_code = 401
        return {"detail": {"status": 2, "msg": "Email is not registered"}}
    elif not user.is_active:
        # response.status_code = 401
        return {"detail": {"status": 3, "msg": "The account is not active"}}
    else:
        accessToken = generate_access_token_reset_pass(user_reset.email)
        user_info = get_user_info_by_email(db, user_reset.email)
        base_url = os.getenv("FRONTEND_DEV_URL")
        url = f'{base_url}/reset_password/?email={user_reset.email}&token={accessToken}'
        email_variables = {
                "user": user_info,
                "reset_url": url
        }
        email_status = send_mail_template(db, user_reset.email, template_id, email_variables)
        if email_status:
            return {"detail": {"status": 1, "msg": "Email password reset sent successfully"}}
        else:
            return {"detail": {"status": 3, "msg": "An error ocurred while sending email"}}

@user_public_routes.post("/user/reset_password", tags=["Usuarios"])
def reset_password(
    user_reset: UserResetPassword, t: str, db: Session = Depends(get_db)
):
    data = validate_token_general(t)
    if data[0] == 403:
        raise HTTPException(status_code=401, detail={"status": 2, "msg": "Token Has expired"})
    if data[0] == 401:
        raise HTTPException(status_code=401, detail={"status": 4, "msg": "Invalid token"})
    try:
        account = db.query(User).filter_by(email=user_reset.email).first()
        new_hashed_password = hash_str(user_reset.password)
        account.hashed_pass = new_hashed_password
        db.add(account)
        db.commit()
    except Exception as ex:
        db.rollback()
        print(f"An error ocurred while changing the password: {ex}")
        raise HTTPException(status_code=500, detail={"status": 3, "msg": "An error ocurred while changing the password"})
    return {"detail": {
        "status": 1,
        "msg": "Password updated successfully"
    }}


@user_public_routes.post("/user/verify/")
def verify_account(t: str, db: Session = Depends(get_db)):
    data = validate_token_general(t)
    if data[0] == 403:
        raise HTTPException(status_code=401, detail={"status": 2, "msg": "Token Has expired"})
    if data[0] == 401:
        raise HTTPException(status_code=401, detail={"status": 4, "msg": "Invalid token"})
    email = data[1]["user_email"]
    try:
        account =  db.query(User).filter_by(email=email).first()
        account.is_active = True
        db.add(account)
        db.commit()
        db.refresh(account)
    except Exception as ex:
        db.rollback()
        print(ex)
        raise HTTPException(status_code=500, detail={"status": 3, "msg": "An error ocurred while verifying the account"})
    return {"detail": {
        "status": 1,
        "msg": "Account verified successfully"
    }}


@user_public_routes.post("/usuario/change_password/{email}", tags=["Usuarios"])
def change_password(
    email: str,
    change_pass: UserChangePassword,
    response: Response,
    db: Session = Depends(get_db),
):
    status_code, resp_token = validate_token_general(change_pass.access_token)

    # Valida token
    if status_code == 403:
        response.status_code = 403
        respuesta = {
            "mensaje": "El tiempo para recuperar contraseña expiro",
            "data": [],
        }
        return respuesta
    elif status_code == 401:
        response.status_code = 401
        return resp_token

    # valida email de token y email enviado
    if email != resp_token["user_email"]:
        response.status_code = 401
        respuesta = {
            "mensaje": "El email no corresponde al token",
            "data": [],
        }
        return respuesta

    exist_email = get_user_by_email(db, email)

    if not exist_email:
        response.status_code = 401
        return {"mensaje": "No email ingresado no esta registrado", "data": ""}
    elif not exist_email.is_active:
        response.status_code = 401
        return {"mensaje": "No email ingresado esta desactivado", "data": ""}

    if change_pass.password != change_pass.password_confirm:
        response.status_code = 401
        respuesta = {
            "mensaje": "Ambas contraseñas no son iguales",
            "data": [],
        }
        return respuesta
    else:
        update_data = {"hashed_pass": hash_str(change_pass.password)}
        respuesta_update_user = crud_update_user_by_email(db, email, update_data)

        if respuesta_update_user != 0:
            response.status_code = 200
            return {
                "mensaje": "La contraseña se ha cambiado correctamente, lo proxima vez que inicie sesion podra usar su nueva contraseña",
                "data": [],
            }
        else:
            response.status_code = 401
            return {
                "mensaje": "Ocurrio un error inesperado, intente de nuevo",
                "data": "",
            }

@user_public_routes.post("/usuario/change_email/{email}", tags=["Usuarios"])
def change_email(
    email: str,
    change_pass: UserChangeEmail,
    response: Response,
    db: Session = Depends(get_db),
):
    status_code, resp_token = validate_token_general(change_pass.access_token)

    # Valida token
    if status_code == 403:
        response.status_code = 403
        respuesta = {
            "mensaje": "El tiempo para cambiar el correo expiro",
            "data": [],
        }
        return respuesta
    elif status_code == 401:
        response.status_code = 401
        return resp_token

    # valida email de token y email enviado
    if email != resp_token["user_email"]:
        response.status_code = 401
        respuesta = {
            "mensaje": "El email no corresponde al token",
            "data": [],
        }
        return respuesta

    exist_email = get_user_by_email(db, email)

    if not exist_email:
        response.status_code = 401
        return {"mensaje": "No email ingresado no esta registrado", "data": ""}
    elif not exist_email.is_active:
        response.status_code = 401
        return {"mensaje": "No email ingresado esta desactivado", "data": ""}

    if change_pass.email != change_pass.email_confirm:
        response.status_code = 401
        respuesta = {
            "mensaje": "Ambos correos no son iguales",
            "data": [],
        }
        return respuesta
    else:
        update_data = {"email": change_pass.email}
        respuesta_update_user = crud_update_user_by_email(db, email, update_data)

        if respuesta_update_user != 0:
            response.status_code = 200
            return {
                "mensaje": "El correo se ha cambiado correctamente, lo proxima vez que inicie sesion podra usar su nuevo correo",
                "data": [],
            }
        else:
            response.status_code = 401
            return {
                "mensaje": "Ocurrio un error inesperado, intente de nuevo",
                "data": "",
            }



@user_routes.get("/search/user/{search}", tags=["Usuarios"])
def get_search_user(search:str, db: Session = Depends(get_db)):
    possible_users  = search_user_by_email(db, search)
    return { "data": possible_users }


@user_routes.delete("/delete_usuario/{user_id}", tags=["Usuarios"])
def delete_user(user_id:str, db: Session = Depends(get_db)):
    response = delete_user_by_id(db, user_id)

    if response == None:
        raise HTTPException(status_code=404, detail="User not found")

    if response['status'] == 3:
        raise HTTPException(status_code=500, detail= response)
    return {"detail": response}
