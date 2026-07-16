import os
from xmlrpc.client import boolean
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import Annotated, Optional
from schema.pagination.pagination_schema import Pagination
from helper.pagination_helpers import pagination_params

from crud.campers.parent_crud import (
    get_all_parent,
    search_all_parent_admin,
    get_all_parent_admin,
    get_parent_by_uuid,
    create_new_parent,
    create_new_parent_user_id,
    update_parent_by_id,
    delete_parent, 
    search_parent_by_name_user,
    get_parent_for_admin_by_id
)    
from crud.camps.camp_crud import (
    get_camp_by_id
)
from crud.camps.location_crud import (
    get_location_by_uuid
)
from crud.camps.camper_in_camp_crud import (
    get_camper_in_camp_by_camper_camp,
    get_camps_name_amount_camper,
    get_past_subscribe_by_camper,
    get_past_due_camps_by_camper
)
from crud.payments.payment_crud import (
    get_payment_by_camper_camp,
    get_camper_payments_in_camp
)
from crud.campers.camper_crud import (
    get_campers_from_parent,
    get_camper_by_uuid
)
from schema.campers.parent_schema import(
    ParentCreate,
    ParentModify,
    ParentCompleteCreate

)

from crud.crud_user import create_new_user, get_user_by_email, create_parent_complete
from utils.db import SessionLocal
from utils.image_tools import img_to_base_64
from utils.payments.payment_table import create_payment_table, get_camper_balance_per_camp, get_camper_total_balance
from utils.pdf.baucher_pago import generar_pdf_baucher
from utils.formatters import format_numbers_commas_currency
from model.catalogs.payment_account import PaymentAccount
from model.catalogs.currency import Currency
from model.camps.camp_payments_accounts import CampPaymentAccount
from model.camps.camp import Camp

CAMP_LOGO_BLACK_FILE_NAME = os.getenv("CAMP_LOGO_BLACK_FILE_NAME")
PAYMENT_REFERENCE_EMAIL = os.getenv("PAYMENT_REFERENCE_EMAIL")

parent_routes = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@parent_routes.get("/parent/", tags=["Campers"])
def get_parent(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db)):
    list_parent = get_all_parent(db, pagination)
    return {"data": list_parent}

@parent_routes.get("/parent/{parent_id}", tags=["Campers"])
def get_parent_by_id(parent_id:str, db: Session = Depends(get_db)):
    list_parent = get_parent_by_uuid(db, parent_id)
    return {"data": list_parent}

@parent_routes.post("/parent/", tags=["Campers"])
def create_parent(new_parent:ParentCreate, db: Session =Depends(get_db)):
    list_parent = create_new_parent(db, new_parent)
    return {"data": list_parent}

# @parent_routes.post("/parent_create/", tags=["Campers"])
# def create_parent_complete(new_parent_complete:ParentCompleteCreate, db: Session =Depends(get_db)):
#     user = get_user_by_email(db, new_parent_complete.user.email)
#     if user:
#         return {"detail": {"status": 2, "msg": "Ya existe una cuenta con ese correo"}}    
#     user = create_new_user(db, new_parent_complete.user)
    
#     if user == None:
#         return {"detail": {"status": 3, "msg": "Ocurrió un error al crear la cuenta"}}
#     parent = create_new_parent_user_id(db, new_parent_complete.parent, user.id)
    
#     if parent == None:
#         return {"detail": {"status": 3, "msg": "Ocurrió un error al crear la cuenta"}}
    
#     return {"detail": {"status": 1, "msg": "Se creó correctamente la cuenta"}}


@parent_routes.post("/parent_create/", tags=["Campers"])
def parent_complete(new_parent_complete:ParentCompleteCreate, db: Session =Depends(get_db)):
    
    result = create_parent_complete(db, new_parent_complete)
    
    if result == 1:
        return {"detail": {"status": 1, "msg": "La cuenta se creo correctamente"}}
    if result == 2:
        return {"detail": {"status": 2, "msg": "Ya existe una cuenta con ese email"}}
    if result == 3:
        raise HTTPException(status_code=500, detail= {"status": 3, "msg": "Ocurrió un error desconocido al crear la cuenta"})
    

@parent_routes.patch("/parent/{parent_id}", tags=["Campers"])
def update_parent(parent_id:str,modify_parent:ParentModify,db: Session = Depends(get_db)):

    update_data = modify_parent.dict(exclude_unset=True)
    print(update_data)
    parent_upcdate_result = update_parent_by_id(db,parent_id,update_data)

    if parent_upcdate_result != 0:
        exist_parent = get_parent_by_uuid(db, parent_id)
        return {"mensaje": "Actualizado Correctamente", "data": exist_parent}
    else:
        return {"mensaje": "Ningun registro fue afectado", "data": ""}
        
@parent_routes.get("/parent_dashboard/{parent_id}", tags=["Campers"])
def parent_dashboard(parent_id:int, db: Session = Depends(get_db)):
    info = []
    parent_total_amount = 0
    list_campers= get_campers_from_parent(db, parent_id)
    for camper in list_campers:
        camps_info = get_camps_name_amount_camper(db, camper.get('id'))
        
        total_balance = get_camper_total_balance(db, camper.get('id'))

        past_camps = get_past_subscribe_by_camper(db, camper.get('id'))
        
        for index, camp_info in enumerate(camps_info):
            camp_info_dict = dict(camp_info)
            balance = get_camper_balance_per_camp(db, camper.get('id'), camp_info.get('camp_id'))
            camp_info_dict["camper_payment_balance"] = balance
            camps_info[index] = camp_info_dict
        
        
        for index, past_camp in enumerate(past_camps):
            past_camp_dict = dict(past_camp)
            balance = get_camper_balance_per_camp(db, camper.get('id'), past_camp.get('camp_id'))
            past_camp_dict["camper_payment_balance"] = balance
            past_camps[index] = past_camp_dict
 
       
        due_past_camps = get_past_due_camps_by_camper(db, camper.get('id'))

        for index, due_past_camp in enumerate(due_past_camps):
            due_past_camp_dict = dict(due_past_camp)
            balance = get_camper_balance_per_camp(db, camper.get('id'), due_past_camp.get('camp_id'))
            due_past_camp_dict["camper_payment_balance"] = balance
            due_past_camps[index] = due_past_camp_dict



        info.append(
            {
                "camper": camper,
                "camper_balance": total_balance,
                "camps": camps_info,
                "due_past_camps": due_past_camps
            }
        )
        parent_total_amount = total_balance
    return{
            "parent_total_amount": parent_total_amount,
            "campers": info            
        }

@parent_routes.get("/parent_camper_in_camp/{camper_id}/{camp_id}", tags=["Campers"])
def parent_camper_in_camp(camper_id:int, camp_id:int,  db: Session = Depends(get_db)):
    camp= get_camp_by_id(db, camp_id)
    location = get_location_by_uuid(db, camp.location_id)
    camper_payments_in_camp =  get_camper_payments_in_camp(db, camper_id, camp_id)
    payments = create_payment_table(db, camper_payments_in_camp)   
    
    balance = 0
    if len(payments) > 0:
        balance = payments[-1]["balance"]
    
    
    # payments= get_payment_by_camper_camp(db, camper_id, camp_id)
    camper_in_camp = get_camper_in_camp_by_camper_camp(db, camper_id, camp_id)

    if camper_in_camp:
        camper_subscribe = True
    else:
        camper_subscribe = False

    if camp.show_payment_parent and camper_subscribe:
        return{"camper_subscribe": camper_subscribe, "camp": camp, "location": location.name,  "payments":payments, "payment_balance": balance}
    else:
        return{"camper_subscribe": camper_subscribe, "camp": camp, "location": location.name}

@parent_routes.delete("/delete_parent/{parent_id}", tags=["Campers"])
def delete_parent_by_id(parent_id:int, db: Session = Depends(get_db)):
    status = delete_parent(db, parent_id)
    return{"status": status}

@parent_routes.get("/search/parent/{search}", tags=["Campers"])
def get_search_parent(search:str, db: Session = Depends(get_db)):
    possible_parents  = search_parent_by_name_user(db, search)
    return { "data": possible_parents }

@parent_routes.get("/payment_boucher/{camper_id}/{camp_id}", response_class=FileResponse, tags=["Campers"])
def get_payment_boucher(camper_id:int, camp_id:int, db:Session= Depends(get_db)):
    camp = get_camp_by_id(db, camp_id)
    camper = get_camper_by_uuid(db, camper_id)
    camper_in_camp = get_camper_in_camp_by_camper_camp(db, camper_id, camp_id)
    
    
    payment_accounts = (
            db.query(
            PaymentAccount.bank,
            PaymentAccount.name.label("name_reference"),
            PaymentAccount.account_number,
            PaymentAccount.clabe_number.label("clabe"),
        ).select_from(PaymentAccount)
        .join(CampPaymentAccount, CampPaymentAccount.paymentaccount_id == PaymentAccount.id)
        .join(Camp, Camp.id == CampPaymentAccount.camp_id)
        .filter(Camp.id == camp_id).all()
    )
    camp_currency = (db.query(Currency).select_from(Currency)
                     .join(Camp, Camp.currency_id == Currency.id).filter(Camp.id == camp_id).first())
    
    
    logo_64 = "data:image/png;base64," + img_to_base_64(f"media/assets/logos/{CAMP_LOGO_BLACK_FILE_NAME}").decode("utf-8")
    context = {
    "name_camping": getattr(camper, "name") + " " + getattr(camper, "lastname_father"),
    "camping_name":  getattr(camp, "name"),
    "amount_total": format_numbers_commas_currency(camp.public_price, camp_currency.symbol, camp_currency.acronyms),
    "logo":logo_64,
    "information_accounts": payment_accounts,
    "pay_reference": camper_in_camp.camper_id,
    "more_info": getattr(camp,"url"),
    "email": PAYMENT_REFERENCE_EMAIL
    }   
    
    path = generar_pdf_baucher(context)
    return FileResponse(path)

@parent_routes.get("/admin/parent/{parent_id}", tags=["Campers"])
def get_parent_for_admin(parent_id:str, db: Session = Depends(get_db)):
    parent = get_parent_for_admin_by_id(db, parent_id)
    return {"data": parent}

@parent_routes.get("/admin/parent/", tags=["Campers"])
async def get_parent_admin(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db)):
    list_parent = get_all_parent_admin(db, pagination)
    return {"data": list_parent}

@parent_routes.get("/search_admin_parent/", tags=["Campers"])
async def get_parent_admin(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db),  tutor_1_name: Optional[str] = '',tutor_1_lastname_father: Optional[str] = '', tutor_1_lastname_mother: Optional[str] = '', tutor_1_email: Optional[str] = '', tutor_2_name: Optional[str] = '', tutor_2_lastname_father: Optional[str] = '',tutor_2_lastname_mother: Optional[str] = '', tutor_2_email: Optional[str] = ''):
    list_parent = search_all_parent_admin(db, pagination, tutor_1_name, tutor_1_lastname_father, tutor_1_lastname_mother, tutor_1_email, tutor_2_name, tutor_2_lastname_father,tutor_2_lastname_mother, tutor_2_email)
    return {"data": list_parent}