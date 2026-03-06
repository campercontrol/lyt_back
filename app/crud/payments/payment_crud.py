import os
from sqlalchemy import case, and_
from sqlalchemy.orm import Session
import traceback
from model.payments import Payment, PaymentTransactionType, PaymentMethod
from model.campers import Camper
from model.campers.parent import Parent
from model.camps import Camp, CamperInCamp
from model.catalogs.currency import Currency

from utils.payments.payment_table import get_payment_table, create_payment_table
from utils.db import db_mapping_rows_to_dict
from helper.mailing_helpers import send_mail_template_payment

from crud.payments.payment_method_crud import get_all_payment_method
from crud.payments.payment_transaction_type_crud import get_all_payment_transaction_type

from crud.mailings.mailing_crud import get_camper_context_massive_mail, get_second_parent_info_mailing_by_camper_id
from crud.campers.parent_crud import get_second_tutor_by_parent_id, get_parent_by_id_mailing

from schema.payments.payment_schema import (
    PaymentCreate,
    PaymentModify,
)

TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID"))
TRANSACTION_TYPE_CAMP_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PAYMENT_ID"))
TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE = int(os.getenv("TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE"))
TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID"))
USER_PARTIAL_PAYMENT_TEMPLATE_ID = int(os.getenv("USER_PARTIAL_PAYMENT_TEMPLATE_ID"))
ADMIN_PARTIAL_PAYMENT_TEMPLATE_ID = int(os.getenv("ADMIN_PARTIAL_PAYMENT_TEMPLATE_ID"))
USER_TOTAL_PAYMENT_TEMPLATE_ID = int(os.getenv("USER_TOTAL_PAYMENT_TEMPLATE_ID"))
CAMP_STATUS_ENROLLED_ID = int(os.getenv("CAMP_STATUS_ENROLLED_ID"))


def get_all_payment(db):
    rows = db.query(Payment).all()
    return rows


def get_payment_by_id(db, payment_id: int):
    return (
        db.query(Payment)
        .filter_by(
            id=payment_id,
        )
        .first()
    )

def create_payment_controller(db: Session, new_payment):
        
    try: 
        camper_id = new_payment.camper_id
        camp_id = new_payment.camp_id
                   
        payment_created = create_new_payment_and_update_balance_transaction(db, new_payment.dict(exclude_unset=True))
        db.commit()
        db.refresh(payment_created)
        
        camper_balance = (db.query(CamperInCamp.payment_balance).select_from(CamperInCamp).filter(and_(CamperInCamp.camper_id == camper_id, CamperInCamp.camp_id == camp_id)).first())
        
        db_payment = get_camper_payment_in_camp_by_payment_id(db, payment_created.id)
        
        formated_payment_amount = "{:,.1f}".format(abs(db_payment.payment_amount))
        
        email_context = get_camper_context_massive_mail(db, camp_id, camper_id)
        email_context["payment"]["payment_date"] = db_payment.payment_date
        email_context["payment"]["payment_method"] = db_payment.payment_method
        email_context["payment"]["amount"] = db_payment.currency_symbol + str(formated_payment_amount) + db_payment.currency_acronym
        email_context["payment"]["txn_type"]  = db_payment.txn_name
        email_context["payment"]["txn_number"] = db_payment.txn_number
        
        camper_payments_in_camp = get_camper_payments_in_camp(db, new_payment.camper_id, new_payment.camp_id)
        payment_table = create_payment_table(db, camper_payments_in_camp)   
        
        email_context["payments"] = payment_table
        
        if camper_balance.payment_balance <= 0:       
            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db, camper_id)
            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
            
        else :
            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db, camper_id)
            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
        
        return 1
    except Exception as ex:
        db.rollback()
        print(f"An error occurred: {type(ex).__name__} – {ex}")
        traceback.print_exc()
        return 3

    
    
def create_new_payment(db, new_payment: PaymentCreate):
    db_payment = None
    try:
        if new_payment["payment_amount"] < 0:
            new_payment["payment_amount"] = new_payment["payment_amount"] * -1
        
        if new_payment["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            new_payment["payment_amount"] = new_payment["payment_amount"] * -1
        
        db_payment = Payment(**new_payment)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
    except Exception as ex:
        db.rollback()
        print(f"An error ocurred while saving new payment {ex}")
    return db_payment    
    
def create_new_payment_transaction(db, new_payment: PaymentCreate):
    if new_payment["payment_amount"] < 0:
        new_payment["payment_amount"] = new_payment["payment_amount"] * -1
    
    if new_payment["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
        new_payment["payment_amount"] = new_payment["payment_amount"] * -1
    
    db_payment = Payment(**new_payment)
    db.add(db_payment)
    db.flush()
    return db_payment   
    
def create_new_payment_and_update_balance(db, new_payment: PaymentCreate):
    camper_id = new_payment["camper_id"]
    camp_id = new_payment["camp_id"]
    camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id)).first()
    try:
        
        if new_payment["payment_amount"] < 0:
            new_payment["payment_amount"] = new_payment["payment_amount"] * -1
        
        if new_payment["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID,TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            new_payment["payment_amount"] = new_payment["payment_amount"] * -1
        
        db_payment = Payment(**new_payment)
        db.add(db_payment)
        db.commit()
        if db_payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            total_balance = abs(camper_in_camp.payment_balance) - abs(float(db_payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp) 
            db.commit()
        else:
            total_balance = abs(camper_in_camp.payment_balance) + abs(float(db_payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp) 
            db.commit()            
        
        db.refresh(db_payment)
    except Exception as ex:
        db_payment = None
        db.rollback()
        print(f"An error ocurred while saving payment: {ex}")    
    return db_payment

def create_new_payment_and_update_balance_transaction(db, new_payment: PaymentCreate):
    camper_id = new_payment["camper_id"]
    camp_id = new_payment["camp_id"]
    camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id)).first()
        
    if new_payment["payment_amount"] < 0:
        new_payment["payment_amount"] = new_payment["payment_amount"] * -1
    
    if new_payment["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
        new_payment["payment_amount"] = new_payment["payment_amount"] * -1
    db_payment = Payment(**new_payment)
    db.add(db_payment)
    db.flush()
    if db_payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
        total_balance = abs(camper_in_camp.payment_balance) - abs(float(db_payment.payment_amount))
        camper_in_camp.payment_balance = total_balance
        db.add(camper_in_camp) 
    else:
        total_balance = abs(camper_in_camp.payment_balance) + abs(float(db_payment.payment_amount))
        camper_in_camp.payment_balance = total_balance
        db.add(camper_in_camp) 
    db.flush()
    return db_payment
    

def delete_payment_and_update_balance_transaction(db: Session, payment_id: int, camper_id):
    payment = get_payment_by_id(db, payment_id)
    camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == payment.camp_id, CamperInCamp.camper_id == camper_id)).first()
    if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
        total_balance = abs(camper_in_camp.payment_balance) + abs(float(payment.payment_amount))
        camper_in_camp.payment_balance = total_balance
        db.add(camper_in_camp)
        db.delete(payment)
    else:
        total_balance = abs(camper_in_camp.payment_balance) - abs(float(payment.payment_amount))
        camper_in_camp.payment_balance = total_balance
        db.add(camper_in_camp) 
        db.delete(payment)        
        
def delete_payment_and_update_balance(db: Session, payment_id: int, camper_id):
    payment = get_payment_by_id(db, payment_id)
    camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == payment.camp_id, CamperInCamp.camper_id == camper_id)).first()
    try:
        if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            total_balance = abs(camper_in_camp.payment_balance) + abs(float(payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp)
            db.delete(payment)
            db.commit()
        else:
            total_balance = abs(camper_in_camp.payment_balance) - abs(float(payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp) 
            db.delete(payment)
            db.commit()            
    except Exception as ex:     
        db.rollback()
        print(f"An error ocurred while saving payment: {ex}")
        return False
    return True            
        
def update_payment_by_id(db, payment_id: int, modify_payment: PaymentModify):
    rows_updated = (
        db.query(Payment)
        .filter_by(id=payment_id)
        .update(modify_payment, synchronize_session="fetch")
    )
    db.commit()
    return rows_updated

        
def update_payment_controller(db, payment_id: int, modify_payment: PaymentModify):
    
    
    try:
        current_payment = db.query(Payment).filter(Payment.id == payment_id).first()
        camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == current_payment.camp_id, CamperInCamp.camper_id == current_payment.camper_id)).first()

        if current_payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            camper_in_camp.payment_balance += abs(current_payment.payment_amount)
        else:
            camper_in_camp.payment_balance -= abs(current_payment.payment_amount)
        
        if modify_payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
            total_balance = abs(camper_in_camp.payment_balance) - abs(float(modify_payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp) 
        else:
            total_balance = abs(camper_in_camp.payment_balance) + abs(float(modify_payment.payment_amount))
            camper_in_camp.payment_balance = total_balance
            db.add(camper_in_camp)
        
        db.query(Payment).filter_by(id=current_payment.id).update(modify_payment.dict(exclude_unset=True), synchronize_session="fetch")
        db.commit()
        db.refresh(camper_in_camp)
        
        payment_updated = get_camper_payment_in_camp_by_payment_id(db, payment_id)
                
        formated_payment_amount = "{:,.1f}".format(abs(payment_updated.payment_amount))
        
        email_context = get_camper_context_massive_mail(db, modify_payment.camp_id, modify_payment.camper_id)
        
        email_context["payment"]["payment_date"] = payment_updated.payment_date
        email_context["payment"]["payment_method"] = payment_updated.payment_method
        email_context["payment"]["amount"] = payment_updated.currency_symbol + str(formated_payment_amount) + payment_updated.currency_acronym
        email_context["payment"]["txn_type"]  = payment_updated.txn_name
        email_context["payment"]["txn_number"] = payment_updated.txn_number
        
        camper_payments_in_camp = get_camper_payments_in_camp(db, modify_payment.camper_id, modify_payment.camp_id)
        payment_table = create_payment_table(db, camper_payments_in_camp)   
        
        email_context["payments"] = payment_table
        
        
        if camper_in_camp.payment_balance <= 0:       
            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db, modify_payment.camper_id)
            send_mail_template_payment(db, email_context["user"]["email"], USER_TOTAL_PAYMENT_TEMPLATE_ID, email_context)
    
        else :
            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
            email_context["user"] = get_second_parent_info_mailing_by_camper_id(db, modify_payment.camper_id)
            send_mail_template_payment(db, email_context["user"]["email"], USER_PARTIAL_PAYMENT_TEMPLATE_ID, email_context)
        
        
        return 1
    except Exception as ex:
        db.rollback()
        print(f"An error occurred: {type(ex).__name__} – {ex}")
        traceback.print_exc()
        return 3

def get_payment_by_camper_camp(db, camper_id: int, camp_id: int):
    #Todo: Refactor to use create_payment_table
    rows = (
        db.query(
            Payment.id.label("id"),
            Payment.payment_amount.label("payment_amount"),
            Payment.payment_date.label("payment_date"),
            Payment.txn_number.label("txn_number"),
            PaymentMethod.name.label("payment_method"),
            PaymentTransactionType.name.label("txn_name"),
        )
        .select_from(Payment)
        .join(PaymentMethod, PaymentMethod.id == Payment.payment_method_id, isouter=True)
        .join(PaymentTransactionType, PaymentTransactionType.id == Payment.txn_type_id)
        .filter(and_(Payment.camper_id == camper_id, Payment.camp_id == camp_id))
        .order_by(Payment.payment_date.asc())
        .all()
    )
    payment_table = get_payment_table(db, rows)

    return payment_table


def get_camper_payment_in_camp_by_payment_id(db: Session, payment_id: int ):
    rows = (
        db.query(
            Payment.id.label("id"),
            Payment.payment_amount,
            Payment.payment_date.label("payment_date"),
            Payment.txn_number.label("txn_number"),
            Payment.txn_type_id,
            PaymentMethod.name.label("payment_method"),
            PaymentTransactionType.name.label("txn_name"),
            Currency.acronyms.label("currency_acronym"),
            Currency.symbol.label("currency_symbol")
        )
        .select_from(Payment)
        .join(PaymentMethod, PaymentMethod.id == Payment.payment_method_id, isouter=True)
        .join(PaymentTransactionType, PaymentTransactionType.id == Payment.txn_type_id)
        .join(Currency, Currency.id == Payment.currency_id)
        .filter(Payment.id == payment_id)
        .order_by(Payment.payment_date.asc())
        .first()
    )


    return rows


def get_camper_payments_in_camp(db, camper_id: int, camp_id: int):
    rows = (
        db.query(
            Payment.id,
            Payment.payment_amount,
            Payment.payment_date,
            Payment.txn_number,
            Payment.txn_type_id,
            PaymentMethod.name.label("payment_method"),
            PaymentTransactionType.name.label("txn_name"),
            Currency.acronyms.label("currency_acronym"),
            Currency.symbol.label("currency_symbol")
        )
        .select_from(Payment)
        .join(PaymentMethod, PaymentMethod.id == Payment.payment_method_id, isouter=True)
        .join(PaymentTransactionType, PaymentTransactionType.id == Payment.txn_type_id)
        .join(Currency, Currency.id == Payment.currency_id)
        .filter(and_(Payment.camper_id == camper_id, Payment.camp_id == camp_id))
        .order_by(Payment.payment_date.asc())
        .all()
    )


    return rows

# imported here due to a circular import
def get_camper_in_camp_by_camper_camp(db: Session, camper_id: int, camp_id: int):
    camper_in_camp = (
        db.query(CamperInCamp)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.camp_id == camp_id,
                CamperInCamp.status == CAMP_STATUS_ENROLLED_ID,
            )
        )
        .first()
    )
    if camper_in_camp:
        return camper_in_camp
    else:
        return False
    
def get_payment_page_camper_in_camp(
    db, camper_id: int, camp_id: int, camper_in_camp_id: int
):
    if camper_id == 0 and camp_id == 0 and camper_in_camp_id == 0:
        transaction_type = get_all_payment_transaction_type(db)
        payment_methods = get_all_payment_method(db)
        return {
            "payment_methods": payment_methods,
            "transaction_type": transaction_type,
        }
        
        
    if (camper_id == 0 or camp_id == 0) and camper_in_camp_id != 0:
        camper_in_camp = (
            db.query(CamperInCamp).filter(CamperInCamp.id == camper_in_camp_id).first()
        )
        camper_id = getattr(camper_in_camp, "camper_id")
        camp_id = getattr(camper_in_camp, "camp_id")

    else:
        camper_in_camp = get_camper_in_camp_by_camper_camp(db, camper_id, camp_id)
        print(camper_in_camp)
        camper_in_camp_id = getattr(camper_in_camp, "id")

    # payment_table = get_payment_by_camper_camp(db, camper_id, camp_id)
    camper_payments_in_camp =  get_camper_payments_in_camp(db, camper_id, camp_id)
    payment_table = create_payment_table(db, camper_payments_in_camp)  
    
    

    camp_name = db.query(Camp.name).filter(Camp.id == camp_id).first()[0]
    camper = (
        db.query(
            (
                Camper.name
                + " "
                + Camper.lastname_father
                + " "
                + Camper.lastname_mother
            ).label("fullname"),
            Camper.parent_id.label("parent_id"),
        )
        .filter(Camper.id == camper_id)
        .first()
    )
    payment_methods = get_all_payment_method(db)
    transaction_type = get_all_payment_transaction_type(db)

    return {
        "payment_methods": payment_methods,
        "transaction_type": transaction_type,
        "camper_name": camper.fullname,
        "camp_name": camp_name,
        "camper_id": camper_id,
        "camp_id": camp_id,
        "camper_in_camp_id": camper_in_camp_id,
        "parent_id": camper.parent_id,
        "payment_balance": camper_in_camp.payment_balance,
        "payment_table": payment_table,
    }


def update_camper_balance_camper(db, camper_id: int, camp_id: int):
    camper_payments = db.query(Payment).filter(
        and_(Payment.camp_id == camp_id, Payment.camper_id == camper_id)).all()
    
    total_balance = 0
    if camper_payments:
        for payment in camper_payments:
            total_balance = total_balance + payment.payment_amount

    db.query(CamperInCamp).filter(
        and_(
            CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id
        )
    ).update({"payment_balance": total_balance})
    db.commit()
    
    return 1

def get_payment_transaction_type_by_movement(db: Session, movement_id):
    query = db.query(PaymentTransactionType.uid, 
                     PaymentTransactionType.id, 
                     PaymentTransactionType.name,
                     PaymentTransactionType.movement).filter(PaymentTransactionType.movement == movement_id)
    data = db.execute(query)
    return data.mappings().first()

def get_all_camper_payments(db: Session, camper_id):
    query = db.query(Payment.id,
                     Payment.payment_amount,
                     Payment.txn_number).filter(Payment.camper_id == camper_id)
    data = db.execute(query)
    data = data.mappings().all()
    return data

def apply_massive_payment(db: Session, camp_id: int, massivePayment):
    campers = massivePayment.campers
    new_payment = dict(massivePayment.payment)
    camp_data = db.query(Camp).filter(Camp.id == camp_id).first()
    new_payment["currency_id"] = camp_data.currency_id
    
    result = True
    for camper in campers:
        camper_in_camp = db.query(CamperInCamp).filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper)).first()
        camper_data = db.query(Camper.id.label("camper_id"), Parent.id.label("parent_id")).select_from(Camper).join(Parent, Parent.id == Camper.parent_id).first()   
        new_payment["parent_id"] = camper_data.parent_id
        new_payment["camper_id"] = camper
        new_payment["camp_id"] = camp_id
        
        try:
            if new_payment["payment_amount"] < 0:
                new_payment["payment_amount"] = new_payment["payment_amount"] * -1
            
            if new_payment["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
                new_payment["payment_amount"] = new_payment["payment_amount"] * -1
            
            db_payment = Payment(**new_payment)
            db.add(db_payment)
            db.commit()
            if db_payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID, TRANSACTION_TYPE_CAMP_PAYMENT_ADVANCE):
                total_balance = abs(camper_in_camp.payment_balance) - abs(float(db_payment.payment_amount))
                camper_in_camp.payment_balance = total_balance
                db.add(camper_in_camp) 
                db.commit()
            else:
                total_balance = abs(camper_in_camp.payment_balance) + abs(float(db_payment.payment_amount))
                camper_in_camp.payment_balance = total_balance
                db.add(camper_in_camp) 
                db.commit()            
            
        except Exception as ex:
            db.rollback()
            result = False
            print(f"An error ocurred while saving payment: {ex}")    
        
    return result
    