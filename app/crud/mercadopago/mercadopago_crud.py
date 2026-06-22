import uuid
import os
import json
import httpx
import traceback
from sqlalchemy import and_
from sqlalchemy.orm import Session
from datetime import date, datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from crud.camps.camp_crud import get_camp_by_id
from crud.payments.payment_crud import get_camper_payment_in_camp_by_payment_id, get_camper_payments_in_camp
from utils.payments.payment_table import get_payment_table, create_payment_table
from crud.mailings.mailing_crud import get_camper_context_massive_mail, get_second_parent_info_mailing_by_camper_id
from helper.mailing_helpers import send_mail_template_payment
from model.campers import Camper, Parent
from model.camps.camp import Camp
from model.catalogs.currency import Currency
from model.mercadopago import MercadopagoMerchantOrder, MercadopagoPayment, MercadopagoPreference
from model.camps.camper_in_camp import CamperInCamp
from utils.db import db_mapping_rows_to_dict
from model.user import User
from model.mercadopago.mercadopago_payment import MercadopagoPayment
from model.mercadopago.mercadopago_merchant_order import MercadopagoMerchantOrder
from model.mercadopago.mercadopago_preference import MercadopagoPreference
from model.mercadopago.mercadopago_seller_credentials import MercadopagoSellerCredentials
from crud.payments.payment_crud import create_new_payment_and_update_balance_transaction
from schema.mercadopago.mercadopago_payment_schema import MercadopagoPaymentCreate, MercadopagoPaymentUpdate
from schema.mercadopago.mercadopago_merchant_order_schema import MercadopagoMerchantOrderCreate
from schema.mercadopago.mercadopago_seller_credentials import MercadopagoSellerCredentials
from schema.payments.payment_schema import PaymentCreate
from decimal import Decimal, ROUND_DOWN
# SDK de Mercado Pago
import mercadopago
# Agrega credenciales
MP_TOKEN = os.getenv("MP_TOKEN")
MP_APP_ID = os.getenv("MP_APP_ID")
USER_PARTIAL_PAYMENT_TEMPLATE_ID = int(os.getenv("USER_PARTIAL_PAYMENT_TEMPLATE_ID"))
USER_TOTAL_PAYMENT_TEMPLATE_ID = int(os.getenv("USER_TOTAL_PAYMENT_TEMPLATE_ID"))
PAYMENT_METHOD_MERCADO_PAGO_ID  = int(os.getenv("PAYMENT_METHOD_MERCADO_PAGO_ID"))
MERCADOPAGO_STATEMENT_DESCRIPTOR = os.getenv("MERCADOPAGO_STATEMENT_DESCRIPTOR")
FRONTEND_PROD_URL = os.getenv("FRONTEND_PROD_URL")
BACKEND_PROD_URL = os.getenv("BACKEND_PROD_URL")
TRANSACTION_TYPE_CAMP_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PAYMENT_ID"))

sdk = mercadopago.SDK(MP_TOKEN)




def get_customer_info(db: Session, camper_id: int):
    query = db.query(Camper.id.label("camper_id"),
                     Camper.name,
                     Camper.lastname_father,
                     Camper.lastname_mother,
                     Parent.id.label("parent_id"),
                     Parent.tutor_name,
                     Parent.tutor_lastname_father,
                     Parent.tutor_lastname_mother,
                     Parent.contact_cellphone,
                     User.id.label("user_id"),
                     User.email,
                     User.created_at.label("user_registration_date"),
                     ).select_from(Camper).join(Parent, Parent.id == Camper.parent_id).join(User, User.id == Parent.user_id).where(Camper.id == camper_id)
    data = db.execute(query)
    data = data.mappings().first()
    return data


def get_camp_info(db: Session, camp_id: int):
    query = db.query(Camp.id,
                     Camp.name,
                     Camp.currency_id,
                     Currency.acronyms,
                     ).select_from(Camp).join(Currency, Currency.id == Camp.currency_id).where(Camp.id == camp_id)
    data = db.execute(query)
    data = data.mappings().first()
    return data

def get_preference(preference_id : str):
    preference_response = sdk.preference().get(preference_id)
    print(preference_response)
    if preference_response["status"] == 404:
        return None
    if preference_response["status"] == 200:
        preference = preference_response["response"]
        return preference
    return None

def get_internal_preference_by_preference_id(db: Session, preference_id: int):
    preference = db.query(MercadopagoPreference).filter(MercadopagoPreference.preference_id == preference_id).first()
    return preference


def get_internal_preference_by_preference_id(db: Session, preference_id: int):
    preference = db.query(MercadopagoPreference).filter(MercadopagoPreference.preference_id == preference_id).first()
    return preference

def get_internal_preference_by_internal_id(db: Session, preference_internal_id: int):
    preference = db.query(MercadopagoPreference).filter(MercadopagoPreference.internal_id == preference_internal_id).first()
    return preference


def get_mercadopago_merchant_order(merchant_order_id : int):
    merchant_order_response = sdk.merchant_order().get(merchant_order_id)
    if merchant_order_response["status"] == 404:
        return None
    if merchant_order_response["status"] == 200:
        merchant_order = merchant_order_response["response"]
        return merchant_order
    return None

def get_internal_merchant_order_by_id(db: Session, merchant_order_id: int):
    merchant_order = db.query(MercadopagoMerchantOrder).filter(MercadopagoMerchantOrder.merchant_order_id == merchant_order_id).first()
    return merchant_order

def get_internal_mercadopago_payment_by_id(db: Session, payment_id: int):
    payment = db.query(MercadopagoPayment).filter(MercadopagoPayment.payment_id == payment_id).first()
    return payment

def get_internal_mercadopago_merchant_order_by_merchant_order_id(db: Session, merchant_order_id: int):
    merchant_order = db.query(MercadopagoMerchantOrder).filter(MercadopagoMerchantOrder.merchant_order_id == merchant_order_id).first()
    return merchant_order

def create_internal_mercadopago_payment(db: Session, new_internal_mercadopago_payment: MercadopagoPaymentCreate): 
    db_internal_mercadopago_payment = MercadopagoPayment(
        **new_internal_mercadopago_payment
        )
    db.add(db_internal_mercadopago_payment)
    db.flush()
    return db_internal_mercadopago_payment

def create_internal_mercadopago_merchant_order(db: Session, new_internal_mercadopago_merchant_order: MercadopagoMerchantOrderCreate): 
    db_internal_mercadopago_merchant_order = MercadopagoMerchantOrder(
        **new_internal_mercadopago_merchant_order
    )
    db.add(db_internal_mercadopago_merchant_order)
    db.flush()
    return db_internal_mercadopago_merchant_order

def update_internal_mercadopago_payment(db, mercadopago_internal_payment_id: int, modify_mercadopago_internal_payment: MercadopagoPaymentUpdate):
    record_updated = (
        db.query(MercadopagoPayment)
        .filter(MercadopagoPayment.id == mercadopago_internal_payment_id)
        .update(modify_mercadopago_internal_payment, synchronize_session="fetch")
    )
    db.commit()
    return record_updated

def get_payment(payment_id : int):
    payment_response = sdk.payment().get(payment_id)
    if payment_response["status"] == 404:
        return None
    if payment_response["status"] == 200:    
        payment = payment_response["response"]
        return payment
    return None

def get_mercado_pago_payments_by_camp_id_and_camper_id(db: Session, camp_id: int, camper_id: int):
    
    camp_camper_mercadopago_payments_query = db.query(MercadopagoPayment.payment_id).filter(and_(MercadopagoPayment.camp_id == camp_id, MercadopagoPayment.camper_id == camper_id))
    camp_camper_mercadopago_payments = db.execute(camp_camper_mercadopago_payments_query)
    camp_camper_mercadopago_payments = camp_camper_mercadopago_payments.mappings().all()
    
    payments = []
    for camp_camper_mercadopago_payment in camp_camper_mercadopago_payments:
        payment = get_payment(camp_camper_mercadopago_payment["payment_id"])
        payments.append(payment)
    return payments     

async def process_mp_notification(db: Session, request: Request):
    
    try: 
        request = await request.json()
        if request["type"] == "payment":
            payment_id = request["data"]["id"]
            mercadopago_payment = get_payment(payment_id)
            internal_mercadopago_payment = get_internal_mercadopago_payment_by_id(db, payment_id)
                
            mercadopago_merchant_order = get_mercadopago_merchant_order(mercadopago_payment["order"]["id"])
            internal_mercadopago_merchant_order = get_internal_mercadopago_merchant_order_by_merchant_order_id(db, mercadopago_merchant_order["id"])

            new_internal_mercadopago_merchant_order = {
                "merchant_order_id": mercadopago_merchant_order["id"],
                "preference_internal_id": mercadopago_merchant_order["external_reference"],
                "status": mercadopago_merchant_order["status"],
                "camper_id": mercadopago_payment["metadata"]["customer"]["camper_id"],
                "camp_id": mercadopago_payment["metadata"]["camp"]["id"]
            }
            if not internal_mercadopago_merchant_order:
                create_internal_mercadopago_merchant_order(db, new_internal_mercadopago_merchant_order)
            else:
                internal_mercadopago_merchant_order.status = mercadopago_merchant_order["status"]
                
            
            internal_payment = {
                
                "paid": True,
                "payment_amount": int(mercadopago_payment["transaction_amount"]),
                "txn_number": "Pago de campamento (Mercadopago)"  + " " + mercadopago_payment["metadata"]["customer"]["name"] + " " +
                mercadopago_payment["metadata"]["customer"]["lastname_father"] + " " + mercadopago_payment["metadata"]["customer"]["lastname_mother"],
                "camp_id": mercadopago_payment["metadata"]["camp"]["id"],
                "payment_date": datetime.now(),
                "payment_method_id": PAYMENT_METHOD_MERCADO_PAGO_ID,
                "camper_id": mercadopago_payment["metadata"]["customer"]["camper_id"],
                "currency_id": mercadopago_payment["metadata"]["camp"]["currency_id"],
                "parent_id": mercadopago_payment["metadata"]["customer"]["parent_id"],
                "txn_type_id": TRANSACTION_TYPE_CAMP_PAYMENT_ID                    
            }                
                
            if not internal_mercadopago_payment:
                new_internal_mercadopago_payment = {    
                    "status" : mercadopago_payment["status"],
                    "payment_id" : mercadopago_payment["id"],
                    "preference_internal_id" : mercadopago_payment["external_reference"],
                    "camper_id" : mercadopago_payment["metadata"]["customer"]["camper_id"],
                    "camp_id" : mercadopago_payment["metadata"]["camp"]["id"]
                
                }
                    
                if mercadopago_payment["status"] == "approved":                    
                    internal_payment_created = create_new_payment_and_update_balance_transaction(db, internal_payment)
                    new_internal_mercadopago_payment["internal_payment_id"] = internal_payment_created.id
                    create_internal_mercadopago_payment(db, new_internal_mercadopago_payment)
                    db.commit()

                    email_context = get_camper_context_massive_mail(db, mercadopago_payment["metadata"]["camp"]["id"], mercadopago_payment["metadata"]["customer"]["camper_id"])
                    camper_balance = (
                        db.query(CamperInCamp.payment_balance)
                        .select_from(CamperInCamp)
                        .filter(and_(CamperInCamp.camper_id == mercadopago_payment["metadata"]["customer"]["camper_id"], CamperInCamp.camp_id == mercadopago_payment["metadata"]["camp"]["id"])).first())

                       
                    db_payment = get_camper_payment_in_camp_by_payment_id(db, internal_payment_created.id)
                    
                    formated_payment_amount = "{:,.1f}".format(abs(db_payment.payment_amount))
                    
                    email_context["payment"]["payment_date"] = db_payment.payment_date
                    email_context["payment"]["payment_method"] = db_payment.payment_method
                    email_context["payment"]["amount"] = db_payment.currency_symbol + str(formated_payment_amount) + db_payment.currency_acronym
                    email_context["payment"]["txn_type"]  = db_payment.txn_name
                    email_context["payment"]["txn_number"] = db_payment.txn_number
                    
                    camper_payments_in_camp = get_camper_payments_in_camp(db, mercadopago_payment["metadata"]["customer"]["camper_id"], mercadopago_payment["metadata"]["camp"]["id"])
                    payment_table = create_payment_table(db, camper_payments_in_camp)   
                    
                    email_context["payments"] = payment_table
                    
                    if camper_balance.payment_balance <= 0:       
                        send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
                        email_context["user"] = get_second_parent_info_mailing_by_camper_id(db,  mercadopago_payment["metadata"]["customer"]["camper_id"])
                        send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
                        
                    else:
                        send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
                        email_context["user"] = get_second_parent_info_mailing_by_camper_id(db,  mercadopago_payment["metadata"]["customer"]["camper_id"])
                        send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
                
                else:
                    create_internal_mercadopago_payment(db, new_internal_mercadopago_payment)
                    db.commit()
                    
            else:
                if mercadopago_payment["status"] == "approved":
                    if internal_mercadopago_payment.internal_payment_id is None:
                        internal_payment_created = create_new_payment_and_update_balance_transaction(db, internal_payment)
                        internal_mercadopago_payment.status = mercadopago_payment["status"]
                        internal_mercadopago_payment.internal_payment_id = internal_payment_created.id
                        db.commit()
                        
                        email_context = get_camper_context_massive_mail(db, mercadopago_payment["metadata"]["camp"]["id"], mercadopago_payment["metadata"]["customer"]["camper_id"])
                        camper_balance = (
                            db.query(CamperInCamp.payment_balance)
                            .select_from(CamperInCamp)
                            .filter(and_(CamperInCamp.camper_id == mercadopago_payment["metadata"]["customer"]["camper_id"], CamperInCamp.camp_id == mercadopago_payment["metadata"]["camp"]["id"])).first())

                        
                        db_payment = get_camper_payment_in_camp_by_payment_id(db, internal_payment_created.id)
                        
                        formated_payment_amount = "{:,.1f}".format(abs(db_payment.payment_amount))
                        
                        email_context["payment"]["payment_date"] = db_payment.payment_date
                        email_context["payment"]["payment_method"] = db_payment.payment_method
                        email_context["payment"]["amount"] = db_payment.currency_symbol + str(formated_payment_amount) + db_payment.currency_acronym
                        email_context["payment"]["txn_type"]  = db_payment.txn_name
                        email_context["payment"]["txn_number"] = db_payment.txn_number
                        
                        camper_payments_in_camp = get_camper_payments_in_camp(db, mercadopago_payment["metadata"]["customer"]["camper_id"], mercadopago_payment["metadata"]["camp"]["id"])
                        payment_table = create_payment_table(db, camper_payments_in_camp)   
                        
                        email_context["payments"] = payment_table
                        
                        if camper_balance.payment_balance <= 0:       
                            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
                            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db,  mercadopago_payment["metadata"]["customer"]["camper_id"])
                            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
                            
                        else:
                            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
                            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db,  mercadopago_payment["metadata"]["customer"]["camper_id"])
                            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
                
                    else:
                        internal_mercadopago_payment.status = mercadopago_payment["status"]
                        db.commit()
                        
            # Here we expire mercadopago preference 
            if mercadopago_payment["status"] == "approved": 
                new_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
                internal_preference = get_internal_preference_by_internal_id(db, mercadopago_payment["external_reference"])
                sdk.preference().update(internal_preference.preference_id, {"expiration_date_to": new_date})
                            

        return 1
    except Exception as ex:
        db.rollback()
        print(f"An error occurred: {type(ex).__name__} – {ex}")
        traceback.print_exc()
        return 3
    
def get_mercadopago_payments_by_customer_id(db: Session, user_id: int):
    query = db.query(MercadopagoPayment).filter(MercadopagoPayment.user_id == user_id)
    data = db.execute(query)
    data = data.mappings().all()
    return data

def get_customer_last_purchase_date(db: Session, user_id:int):
    query = db.query(MercadopagoPayment).filter(MercadopagoPayment.user_id == user_id).order_by(MercadopagoPayment.created_at.desc()).first()
    if query:
        return query.created_at
    return None


def get_marketplace_fee(amount: int):
    marketplace_fee = (0.15 / 100) * amount
    IVA = (16 / 100) * marketplace_fee
    total_marketplace_fee = round(marketplace_fee + IVA, 2)
    return total_marketplace_fee



def get_mercadopago_seller_credentials(db: Session, code: str, state: str):
    try:
        print("=============CODE AND STATE================")
        print("code: ", code)
        print("state: ", state)
        return 1
    except Exception as ex:
        print("=============EXCEPTION================")
        print(ex)
        return 3


    

def create_mercadopago_preference(db: Session, camp_id: int, camper_id: int, customer_defined_amount: float):
    try:
        camp_info = get_camp_info(db, camp_id) 
        customer_info = get_customer_info(db, camper_id)
        user_payments = get_mercadopago_payments_by_customer_id(db, customer_info['user_id'])
        customer_last_purchase_date = get_customer_last_purchase_date(db, customer_info['user_id'])
        
        customer_defined_amount = Decimal(str(customer_defined_amount)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        customer_defined_amount = float(customer_defined_amount)
        # Set marketplace fee to 0 due to kincamp tax issue
        marketplace_fee = get_marketplace_fee(customer_defined_amount)
        # marketplace_fee = 0
        marketplace_id = f'MP-MKP-{MP_APP_ID}'
        customer_info_dict = dict(customer_info)   
        
        customer_info_dict['user_registration_date'] = customer_info_dict['user_registration_date'].strftime('%Y-%m-%dT%H:%M:%S%z')
                        
        if customer_last_purchase_date:
            customer_last_purchase_date = customer_last_purchase_date.strftime('%Y-%m-%dT%H:%M:%S%z')

        id = uuid.uuid4()
        id = str(id)
        metadata = {
            "customer": customer_info_dict,
            "camp": dict(camp_info)
        }  
        request = {
            "items": [
                {
                    "id": id,
                    "title": camp_info['name'],
                    "description": camp_info['name'] + " - " + customer_info['name'] + " " + customer_info['lastname_father'] + " " + customer_info['lastname_mother'],
                    "currency_id": camp_info['acronyms'],
                    "unit_price": customer_defined_amount,
                    "quantity": 1
                }
            ],
            "marketplace_fee": marketplace_fee,
            "payer": {
                "name": customer_info['tutor_name'],
                "surname": customer_info['tutor_lastname_father'] + customer_info['tutor_lastname_mother'],
                "email": customer_info['email'],
                "is_prime_user": False,
                "registration_date": customer_info_dict['user_registration_date'],
                "is_first_purchase_online": True if user_payments == [] else False,
                "last_purchase": customer_last_purchase_date,
                "authentication_type": "Web Nativa",
                "phone": {
                    "number": customer_info['contact_cellphone'],
                },
                # "identification": {
                #     "type": "CPF",
                #     "number": "19119119100",
                # },
                # "address": {
                #     "zip_code": "",
                #     "street_name": "Street",
                #     "street_number": 123,
                # },

            },
            "back_urls": {
                "success": f"{FRONTEND_PROD_URL}/mercado_pago_success",
                "failure": f"{FRONTEND_PROD_URL}/mercado_pago_failure",
                "pending": f"{FRONTEND_PROD_URL}/mercado_pago_pending",
            },
            # "differential_pricing": {
            #     "id": 1,
            # },
            "expires": True,
            # "additional_info": "Discount: 12.00",
            "auto_return": "all",
            "binary_mode": False,
            "external_reference": id,
            "marketplace": marketplace_id,
            "notification_url": f"{BACKEND_PROD_URL}/mercado_pago/notify?source_news=webhooks",
            # "operation_type": "regular_payment",
            "payment_methods": {
                # "default_payment_method_id": "master",
                # "excluded_payment_types": [
                #     {
                #         "id": "ticket",
                #     },
                # ],
                # "excluded_payment_methods": [
                #     {
                #         "id": "",
                #     },
                # ],
                "installments": 3,
                "default_installments": 1,
            },
            "metadata": metadata,
            "statement_descriptor": MERCADOPAGO_STATEMENT_DESCRIPTOR,
        }
        preference_response = sdk.preference().create(request)
        preference = preference_response["response"]
        print(preference)
        mercadopago_internal_preference = MercadopagoPreference(
            preference_id= preference["id"],
            internal_id = preference["external_reference"],
            camper_id = camper_id,
            camp_id = camp_id
        )
        db.add(mercadopago_internal_preference)
        db.commit()
    except Exception as ex:
        db.rollback()
        print(f"An error occurred: {type(ex).__name__} – {ex}")
        traceback.print_exc()
        return None
    return preference

async def refresh_mercadopago_seller_credentials(client_secret: str, grant_type: str, refresh_token: str, db: Session):
    try:
        response = await httpx.AsyncClient().post("https://api.mercadopago.com/oauth/token", data={
            "client_secret": client_secret,
            "grant_type": grant_type,
            "refresh_token": refresh_token
        })
        if response.status_code != 200:
            return response.json()
        else:
            token = response.json()
            mercadopago_seller_credentials = MercadopagoSellerCredentials(
                access_token=token["access_token"],
                token_type=token["token_type"],
                expires_in=token["expires_in"],
                scope=token["scope"],
                user_id=token["user_id"],
                refresh_token=token["refresh_token"],
                public_key=token["public_key"],
                live_mode=token["live_mode"]
            )
            db.commit(mercadopago_seller_credentials)
            return mercadopago_seller_credentials
    except Exception as ex:
        print(ex)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )