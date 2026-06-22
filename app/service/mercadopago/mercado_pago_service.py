from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Response, status
from sqlalchemy.orm import Session
from model.mercadopago import MercadopagoPayment, MercadopagoMerchantOrder
from schema.mercadopago.mercadopago_seller_credentials import MercadopagoSellerCredentials
from crud.mercadopago.mercadopago_crud import create_mercadopago_preference, get_mercadopago_merchant_order, get_payment, process_mp_notification, get_preference, get_mercadopago_seller_credentials, refresh_mercadopago_seller_credentials
from utils.db import SessionLocal

mercadopago_routes = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@mercadopago_routes.get("/mercado_pago/create_payment_link/{camp_id}/{camper_id}/{customer_defined_amount}", tags=["mercadopago"])
def create_preference(camp_id : int, camper_id: int, customer_defined_amount: float, db: Session = Depends(get_db)):
    response = create_mercadopago_preference(db, camp_id, camper_id, customer_defined_amount)
    if response == None:
        raise HTTPException(status_code=500, detail={"status": 3, "msg": "Ocurrió un error al crear la preferencia"})
    return response
    

@mercadopago_routes.post("/mercado_pago/notify", tags=["mercadopago"])
async def mercado_pago_payment_notification(request: Request, id: Optional[int] = None, topic: Optional[str] = None, db:Session = Depends(get_db)):
    result = await process_mp_notification(db, request)
    if result == 3:
        raise HTTPException(status_code=500, detail={"msg": "An error ocurred"})       
    if result == 1:
        return {"status": 1, "msg": "Notification received"}


@mercadopago_routes.get("/mercado_pago/seller/credentials", tags=["mercadopago"])
def mercado_pago_seller_credentials(code: Optional[str] = None, state: Optional[str] = None, db:Session = Depends(get_db)):
    result = get_mercadopago_seller_credentials(db, code, state)  
    if result == 1:
        return {"status": 1, "msg": "Credentials saved successfully"}
    if result == 3:
        return HTTPException(status_code=500, detail={"msg": "An error ocurred"})  


@mercadopago_routes.get("/mercadopago/merchant_order/{merchant_order_id}", tags=["mercadopago"])
def mercadopago_merchant_order(merchant_order_id: int, request: Request):
    response = get_mercadopago_merchant_order(merchant_order_id)
    return response

@mercadopago_routes.get("/mercadopago/preference/{preference_id}", tags=["mercadopago"])
def preference(preference_id: str, request: Request):
    response = get_preference(preference_id)
    return response


@mercadopago_routes.get("/mercadopago/payment/{payment_id}", tags=["mercadopago"])
def mercadopago_payment_id(payment_id: int, request: Request):
    response = get_payment(payment_id)
    return response
    
    

    