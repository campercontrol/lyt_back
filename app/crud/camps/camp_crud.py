import os
import traceback
import sys
from sqlalchemy import and_, func, extract, select, desc,asc, or_, text
from math import ceil
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased
from utils.db import db_mapping_rows_to_dict
from utils.formatters import format_numbers_commas_currency
from datetime import date, datetime
from model.camps import Camp, Location, CampPaymentAccount, CamperInCamp
from model.campers.camper_extra_answer import CamperExtraAnswer
from model.campers.camper_comment import CamperComment
from model.campers import Camper
from model.campers.parent import Parent
from model.user import User
from model.payments.payment import Payment
from model.payments.payment_transaction_type import PaymentTransactionType
from model.payments.payment_method import PaymentMethod
from model.payments.camper_extra_charge import CamperExtraCharge
from model.camps.staff_in_camp import StaffInCamp
from model.staffs.staff import Staff
from model.medical.medical_camper_visit import MedicalCamperVisit
from model.camps.camp_extra_charge import CampExtraCharge
from model.camps.camp_extra_question import CampExtraQuestion
from model.catalogs import (
    Constant
)
from model.campers import (
    School    
)
from model.catalogs.currency import Currency
from schema.camps.camp_schema import CampCreate, CampModify
from schema.pagination.pagination_schema import Pagination, SortEnum
from crud.campers.camper_crud import get_pathological_background_by_camper, get_camper_licensed_medicine, get_extra_charge_by_camper_camp, get_camper_vaccines
from crud.camps.camper_in_camp_crud import get_campers_for_module_count
from crud.camps.staff_in_camp_crud import get_staff_volunteer_in_camp_count, get_staff_in_camp_count
from crud.campers_catalogs.camper_food_restriction_crud import get_camper_food_restriction
from crud.campers.camper_comment_crud import get_camper_comment_by_camper_for_admin, get_camper_comment_by_camper_for_parent, get_camper_comment_by_camper_for_school
from crud.staff_catalogs.staff_food_restriction_crud import get_all_staff_food_restriction_by_id
from crud.staff_catalogs.staff_vaccine_crud import get_staff_all_vaccines_by_staff_id
from crud.groupings.grouping_camp_crud import get_camper_groupings_by_camper_id_and_camp_id
from crud.payments.payment_crud import delete_payment_and_update_balance_transaction, create_new_payment_and_update_balance_transaction
from helper.pagination_helpers import pagination_params, get_number_of_pages
from crud.campers.camper_extra_answer_crud import get_extra_answer_by_camper_camp


BACKEND_DEV_URL = os.getenv("BACKEND_DEV_URL")
PAYPAL_LINK_URL = os.getenv("PAYPAL_LINK_URL")
CAMP_STATUS_ENROLLED_ID = int(os.getenv("CAMP_STATUS_ENROLLED_ID"))
TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID"))
TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID")) 
TRANSACTION_TYPE_CAMP_PRICE_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PRICE_ID"))
TRANSACTION_TYPE_CAMP_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PAYMENT_ID"))
TRANSACTION_TYPE_CAMP_REFUND_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_REFUND_ID"))
TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID"))
TRANSACTION_TYPE_CAMP_STORE_PAYMENT = int(os.getenv("TRANSACTION_TYPE_CAMP_STORE_PAYMENT"))





def get_camp_insr_report(db: Session, camp_id: int):
    catalog_gender = aliased(Constant)
    catalog_camp_enrollment = aliased(Constant)
    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      Camper.birthday,
                      func.concat(extract('year', func.age(func.current_date(), Camper.birthday)), " years ",  extract('month', func.age(func.current_date(), Camper.birthday)), " months ").label("Age"),
                      catalog_gender.value.label('gender'),
                      catalog_camp_enrollment.value.label("enrollment")
                      ).select_from(CamperInCamp)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .join(catalog_gender, Camper.gender_id == catalog_gender.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()
    
    return campers


def get_camp_incomes(db: Session, camp_id: int):
    camp_and_camper_payments_info = {}
    payment_methods = db.query(PaymentMethod).all()
    camp_info = (
        db.query(Camp.id, Currency.symbol, Currency.acronyms)
        .select_from(Camp)
        .join(Currency, Currency.id == Camp.currency_id)
        .filter(Camp.id == camp_id).first()
    )
    incomes_per_payment_method = []
    for payment_method in payment_methods:
        total_payment_amount = (
            db.query(func.sum(func.abs(Payment.payment_amount)))
            .select_from(Payment)
            .filter(Payment.camp_id == camp_id, Payment.payment_method_id == payment_method.id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id ==TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID)).scalar()
        
        )
        total_transactions_per_payment_method = (
            db.query(func.count(Payment.id))
            .select_from(Payment)
            .filter(Payment.camp_id == camp_id, Payment.payment_method_id == payment_method.id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID)).scalar()
            
        )

        
        income = {
            "payment_method": payment_method.name,
            "transactions": total_transactions_per_payment_method,
            "total_amount": format_numbers_commas_currency(total_payment_amount or 0, camp_info.symbol, camp_info.acronyms)
        }
        incomes_per_payment_method.append(income)
    
    total_discount_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID)).scalar()   
    total_transactions_per_discount = db.query(func.count(Payment.id)).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID)).scalar()

    discount_income = {
        "payment_method": "Descuentos",
        "transactions": total_transactions_per_discount,
        "total_amount": format_numbers_commas_currency(total_discount_amount or 0, camp_info.symbol, camp_info.acronyms)
    }
    
    total_refunds_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_REFUND_ID)).scalar()   
    total_transactions_per_refunds = db.query(func.count(Payment.id)).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID)).scalar()
    
    total_refunds = {
        "payment_method": "Reembolsos",
        "transactions": total_transactions_per_refunds,
        "total_amount": format_numbers_commas_currency(total_refunds_amount or 0, camp_info.symbol, camp_info.acronyms)
    }
    
    
    incomes_per_payment_method.append(total_refunds)
    
    campers_in_camp = db.query(CamperInCamp.id, CamperInCamp.payment_balance, CamperInCamp.camp_id, CamperInCamp.camper_id, Constant.value).select_from(CamperInCamp).join(Constant, Constant.id == CamperInCamp.status).filter(CamperInCamp.camp_id == camp_id).all()
    if campers_in_camp:

        campers_and_payments_info = []
        for camper in campers_in_camp:
            camper_payments_by_method = []
            camper_payments_info = {}
            payment_info = {}
            camper_info = db.query(Camper).select_from(Camper).filter(Camper.id == camper.camper_id).first()
            for payment_method in payment_methods:
                camper_payments_by_payment_method_total_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(Payment.camper_id == camper.camper_id, Payment.camp_id == camp_id, Payment.payment_method_id == payment_method.id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID)).scalar()
                camper_total_transactions_by_payment_method = db.query(func.count(Payment.id)).select_from(Payment).filter(Payment.camper_id == camper.camper_id, Payment.camp_id == camp_id, Payment.payment_method_id == payment_method.id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID)).scalar()
                camper_payment_by_method_id = {
                    "id": payment_method.id,
                    "payment_method": payment_method.name,
                    "total_amount": format_numbers_commas_currency(camper_payments_by_payment_method_total_amount or 0, camp_info.symbol, camp_info.acronyms),
                    "transactions": camper_total_transactions_by_payment_method or 0
                }
                camper_payments_by_method.append(camper_payment_by_method_id)
            # camper comments
            total_camper_comments = db.query(func.count(CamperComment.id)).select_from(CamperComment).filter(CamperComment.camper_id == camper.camper_id).scalar() 
            # total_amount, and count of all payments
            camper_payments_total_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(Payment.camper_id == camper.camper_id, Payment.camp_id == camp_id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID)).scalar()
            camper_payments_total_transactions = db.query(func.count(Payment.id)).select_from(Payment).filter(and_(Payment.camper_id == camper.camper_id, Payment.camp_id == camp_id, or_(Payment.txn_type_id == TRANSACTION_TYPE_CAMP_PAYMENT_ID, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_STORE_PAYMENT, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID))).scalar()

            total_payments = {
                "amount": format_numbers_commas_currency(camper_payments_total_amount or 0, camp_info.symbol, camp_info.acronyms),
                "number_of_payments": camper_payments_total_transactions or 0
            }
            #total amount of discounts by camper
            camper_total_discount_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.camper_id == camper.camper_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID)).scalar()   
            camper_total_transactions_per_discount = db.query(func.count(Payment.id)).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.camper_id == camper.camper_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID)).scalar()

            discounts = {
                "amount": format_numbers_commas_currency(camper_total_discount_amount or 0, camp_info.symbol, camp_info.acronyms), 
                "number_of_discounts": camper_total_transactions_per_discount or 0
            }
            
            #total amount of refunds
            camper_total_refund_amount = db.query(func.sum(func.abs(Payment.payment_amount))).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.camper_id == camper.camper_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_REFUND_ID)).scalar() 
            camper_total_refund_transactions = db.query(func.count(Payment.id)).select_from(Payment).filter(and_(Payment.camp_id == camp_id, Payment.camper_id == camper.camper_id, Payment.txn_type_id == TRANSACTION_TYPE_CAMP_REFUND_ID)).scalar()

            refunds = {
                "amount": format_numbers_commas_currency(camper_total_refund_amount or 0, camp_info.symbol, camp_info.acronyms),
                "number_of_refunds": camper_total_refund_transactions or 0
            }
            camp_status = {
                "balance": format_numbers_commas_currency(camper.payment_balance or 0, camp_info.symbol, camp_info.acronyms),
                "enrolment_status": camper.value
            }
            
            payment_info["payments_by_payment_method"] = camper_payments_by_method
            payment_info["total_payments"] = total_payments
            payment_info["discounts"] = discounts
            payment_info["refunds"] = refunds
            payment_info["camp_status"] = camp_status
            
            camper_payments_info["camper_id"] = camper_info.id
            camper_payments_info["camper_fullname"] = camper_info.name + " " + camper_info.lastname_father + " " + camper_info.lastname_mother
            camper_payments_info["number_of_comments"] = total_camper_comments
            camper_payments_info["payments_info"] = payment_info

            campers_and_payments_info.append(camper_payments_info)
            
            camp_and_camper_payments_info["camp_incomes_per_payment_method"] = incomes_per_payment_method
            camp_and_camper_payments_info["camper_payments"] = campers_and_payments_info
    else:
        camp_and_camper_payments_info["camp_incomes_per_payment_method"] = incomes_per_payment_method
        camp_and_camper_payments_info["camper_payments"] = []
    
    
    return camp_and_camper_payments_info
    
        
def get_camp_contact_report(db: Session, camp_id: int):
    
    catalog_camp_enrollment = aliased(Constant)
    
    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      Parent.tutor_name,
                      Parent.tutor_lastname_father,
                      Parent.tutor_lastname_mother,
                      Parent.tutor_cellphone,
                      Parent.tutor_home_phone,
                      Parent.tutor_work_phone,
                      User.email.label("tutor_email"),
                      Parent.contact_name.label("second_tutor_name"),
                      Parent.contact_lastname_father.label("second_tutor_mothers_lastname"),
                      Parent.contact_lastname_mother.label("second_tutor_fathers_lastname"),
                      Parent.contact_cellphone.label("second_tutor_cellphone"),
                      Parent.contact_home_phone.label("second_tutor_fathers_lastname"),
                      Parent.contact_work_phone.label("second_tutor_work_phone"),
                      Parent.contact_email.label("second_tutor_email"),
                      Camper.contact_name.label("emergency_contact"),
                      Camper.contact_relation.label("emergency_contact_kinship"),
                      Camper.contact_homephone.label("emergency_contact_phone"),
                      Camper.contact_cellphone.label("emergency_contact_cellphone"),
                      catalog_camp_enrollment.value.label("enrollment")                      
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .join(Parent, Camper.parent_id == Parent.id)
             .join(User, Parent.user_id == User.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()
    return campers


def get_camp_medical_report(db: Session, camp_id: int):

    catalog_gender = aliased(Constant)
    catalog_swim =  aliased(Constant)
    catalog_blood_type =  aliased(Constant)
    catalog_camp_enrollment = aliased(Constant)

    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      func.concat(extract('year', func.age(func.current_date(), Camper.birthday)), " years ",  extract('month', func.age(func.current_date(), Camper.birthday)), " months ").label("Age"),
                      Camper.height,
                      Camper.weight,
                      catalog_gender.value.label('gender'),
                      catalog_swim.value.label('swim'),
                      Camper.affliction,
                      catalog_blood_type.value.label('blood_type'),
                      Camper.heart_problems,
                      Camper.psicology_treatments,
                      Camper.prevent_activities,
                      Camper.other_allergies,
                      Camper.nocturnal_disorders,
                      Camper.phobias,
                      Camper.drugs,
                      Camper.doctor_precall,
                      Camper.prohibited_foods,
                      Camper.insurance,
                      Camper.insurance_number,
                      Camper.security_social_number,
                      Parent.tutor_name,
                      Parent.tutor_lastname_father,
                      Parent.tutor_lastname_mother,
                      Parent.tutor_cellphone,
                      Parent.tutor_home_phone,
                      Parent.tutor_work_phone,
                      User.email.label("tutor_email"),
                      Parent.contact_name.label("second_tutor_name"),
                      Parent.contact_lastname_father.label("second_tutor_mothers_lastname"),
                      Parent.contact_lastname_mother.label("second_tutor_fathers_lastname"),
                      Parent.contact_cellphone.label("second_tutor_cellphone"),
                      Parent.contact_home_phone.label("second_tutor_fathers_lastname"),
                      Parent.contact_work_phone.label("second_tutor_work_phone"),
                      Parent.contact_email.label("second_tutor_email"),
                      Camper.contact_name.label("emergency_contact"),
                      Camper.contact_relation.label("emergency_contact_kinship"),
                      Camper.contact_cellphone.label("emergency_contact_cellphone"),
                      Camper.contact_homephone.label("emergency_home_phone"),
                      catalog_camp_enrollment.value.label("enrollment")                      
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_gender, Camper.gender_id == catalog_gender.id)
             .join(catalog_swim, Camper.can_swim == catalog_swim.id)
             .join(catalog_blood_type, Camper.blood_type == catalog_blood_type.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .join(Parent, Camper.parent_id == Parent.id)
             .join(User, Parent.user_id == User.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()
    
    campers_report = []
   
    for camper in campers:
        camper_dict = dict(camper)
        camper_pathological_background = get_pathological_background_by_camper(db, camper.id) 
        camper_food_restriction = get_camper_food_restriction(db, camper.id)
        camper_licensed_medicine = get_camper_licensed_medicine(db, camper.id)
        camper_vaccines = get_camper_vaccines(db, camper.id)
        
        for pathological_background in camper_pathological_background:
            camper_dict[pathological_background["name"]] = pathological_background["is_active"]
        
        for food_restriction in camper_food_restriction:
            camper_dict[food_restriction["name"]] = food_restriction["is_active"]
        
        for vaccines in camper_vaccines:
            camper_dict[vaccines["name"]] = vaccines["is_active"]
            
        for licensed_medicine in camper_licensed_medicine:
            camper_dict[licensed_medicine["name"]] = licensed_medicine["is_active"]
            
        campers_report.append(camper_dict)
    
    return campers_report
    


def get_camp_gnl_report(db: Session, camp_id: int):

    catalog_gender = aliased(Constant)
    catalog_grade = aliased(Constant)
    catalog_swim =  aliased(Constant)
    catalog_blood_type =  aliased(Constant)
    catalog_camp_enrollment = aliased(Constant)



    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      Camper.birthday,
                      Camper.height,
                      Camper.weight,
                      catalog_gender.value.label('gender'),
                      catalog_grade.value.label('grade'),
                      School.name.label("school"),
                      Camper.school_other,
                      catalog_swim.value.label('swim'),
                      Camper.affliction,
                      catalog_blood_type.value.label('blood_type'),
                      Camper.heart_problems,
                      Camper.psicology_treatments,
                      Camper.prevent_activities,
                      Camper.other_allergies,
                      Camper.nocturnal_disorders,
                      Camper.phobias,
                      Camper.drugs,
                      Camper.doctor_precall,
                      Camper.prohibited_foods,
                      Camper.comments_admin,
                      Camper.insurance_company,
                      Camper.insurance_number,
                      Camper.security_social_number,
                      Parent.tutor_name,
                      Parent.tutor_lastname_father,
                      Parent.tutor_lastname_mother,
                      Parent.tutor_cellphone,
                      Parent.tutor_home_phone,
                      Parent.tutor_work_phone,
                      User.email.label("tutor_email"),
                      Parent.contact_name.label("second_tutor_name"),
                      Parent.contact_lastname_father.label("second_tutor_father_lastname"),
                      Parent.contact_lastname_mother.label("second_tutor_mother_lastname"),
                      Parent.contact_cellphone.label("second_tutor_cellphone"),
                      Parent.contact_home_phone.label("second_tutor_home_phone"),
                      Parent.contact_work_phone.label("second_tutor_work_phone"),
                      Parent.contact_email.label("second_tutor_email"),
                      Camper.contact_name.label("emergency_contact"),
                      Camper.contact_relation.label("contact_kinship"),
                      Camper.contact_cellphone,
                      Camper.contact_homephone,
                      CamperInCamp.payment_balance,
                      Camper.created_at.label("registration_date"),
                      catalog_camp_enrollment.value.label("enrollment")
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_gender, Camper.gender_id == catalog_gender.id)
             .join(catalog_grade, Camper.grade == catalog_grade.id)
             .join(catalog_swim, Camper.can_swim == catalog_swim.id)
             .join(catalog_blood_type, Camper.blood_type == catalog_blood_type.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .join(Parent, Camper.parent_id == Parent.id)
             .join(User, Parent.user_id == User.id)
             .join(School, Camper.school_id== School.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()

    campers_report = []
   
    for camper in campers:
        camper_dict = dict(camper)
        camper_pathological_background = get_pathological_background_by_camper(db, camper.id) 
        camper_food_restriction = get_camper_food_restriction(db, camper.id)
        camper_licensed_medicine = get_camper_licensed_medicine(db, camper.id)
        camper_vaccines = get_camper_vaccines(db, camper.id)
        camper_extra_charges = get_extra_charge_by_camper_camp(db, camper.id, camp_id)
        camper_parent_comments = get_camper_comment_by_camper_for_parent(db, camper.id)
        camper_school_comments = get_camper_comment_by_camper_for_school(db, camper.id)
        camper_admin_comments = get_camper_comment_by_camper_for_admin(db, camper.id)
        camper_groupings = get_camper_groupings_by_camper_id_and_camp_id(db, camper.id, camp_id)
        camper_extra_answers = get_extra_answer_by_camper_camp(db, camper.id, camp_id)
        
        
        for pathological_background in camper_pathological_background:
            camper_dict[pathological_background["name"]] = pathological_background["is_active"]
        
        for food_restriction in camper_food_restriction:
            camper_dict[food_restriction["name"]] = food_restriction["is_active"]
        
        for vaccines in camper_vaccines:
            camper_dict[vaccines["name"]] = vaccines["is_active"]
            
        for licensed_medicine in camper_licensed_medicine:
            camper_dict[licensed_medicine["name"]] = licensed_medicine["is_active"]
            
        for extra_charge in camper_extra_charges:
            extracharge_column_name = f"{extra_charge['name']} ${extra_charge['price']}"
            camper_dict[extracharge_column_name] = extra_charge["is_selected"]
        
        camper_dict["Comments (Parent)"] = camper_parent_comments
        camper_dict["Comments (Staff)"] = camper_admin_comments
        camper_dict["Comments (School)"] = camper_school_comments
        camper_dict["Groupings"] = camper_groupings
        camper_dict["Camper extra questions"] = camper_extra_answers
        campers_report.append(camper_dict)
        
    return campers_report

def get_camp_food_report(db: Session, camp_id: int):

    catalog_camp_enrollment = aliased(Constant)
    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      Camper.other_allergies,
                      Camper.prohibited_foods,
                      catalog_camp_enrollment.value.label("enrollment")
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()

    campers_report = []
   
    for camper in campers:
        camper_dict = dict(camper)
        camper_food_restriction = get_camper_food_restriction(db, camper.id)
        
        for food_restriction in camper_food_restriction:
            camper_dict[food_restriction["name"]] = food_restriction["is_active"]
        
        campers_report.append(camper_dict)
        
    return campers_report

def get_camp_social_report(db: Session, camp_id: int):

    catalog_gender = aliased(Constant)
    catalog_grade = aliased(Constant)
    catalog_swim =  aliased(Constant)
    catalog_camp_enrollment = aliased(Constant)

    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      Camper.birthday,
                      catalog_gender.value.label('gender'),
                      catalog_grade.value.label('grade'),
                      Camper.prevent_activities,
                      Camper.psicology_treatments,
                      Camper.nocturnal_disorders,
                      Camper.phobias,
                      Camper.drugs,
                      catalog_swim.value.label('swim'),
                      catalog_camp_enrollment.value.label("enrollment")
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_gender, Camper.gender_id == catalog_gender.id)
             .join(catalog_grade, Camper.grade == catalog_grade.id)
             .join(catalog_swim, Camper.can_swim == catalog_swim.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()

    campers_report = []
   
    for camper in campers:
        camper_dict = dict(camper)
        camper_parent_comments = get_camper_comment_by_camper_for_parent(db, camper.id)
        camper_school_comments = get_camper_comment_by_camper_for_school(db, camper.id)
        camper_admin_comments = get_camper_comment_by_camper_for_admin(db, camper.id)
                
        camper_dict["Comments (Parent)"] = camper_parent_comments
        camper_dict["Comments (Staff)"] = camper_admin_comments
        camper_dict["Comments (School)"] = camper_school_comments
        campers_report.append(camper_dict)
        
    return campers_report

def get_camp_extras_report(db: Session, camp_id: int):
    
    catalog_camp_enrollment = aliased(Constant)
    query = (db.query(Camper.id,
                      Camper.name,
                      Camper.lastname_father,
                      Camper.lastname_mother,
                      CamperInCamp.payment_balance,
                      catalog_camp_enrollment.value.label("enrollment")
                      ).select_from(CamperInCamp)
             .join(Camp, CamperInCamp.camp_id == Camp.id)
             .join(Camper, CamperInCamp.camper_id == Camper.id)
             .join(catalog_camp_enrollment, CamperInCamp.status == catalog_camp_enrollment.id)
             .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)))
    campers = db.execute(query)
    campers = campers.mappings().all()

    campers_report = []
   
    for camper in campers:
        camper_dict = dict(camper)

        camper_extra_charges = get_extra_charge_by_camper_camp(db, camper.id, camp_id)
         
        for extra_charge in camper_extra_charges:
            extracharge_column_name = f"{extra_charge['name']} ${extra_charge['price']}"
            camper_dict[extracharge_column_name] = extra_charge["is_selected"]

        campers_report.append(camper_dict)
        
    return campers_report


def get_camp_medical_visit_report(db: Session, camp_id: int):
    query = (db.query(
                        func.concat(Camper.name, ' ', Camper.lastname_father, ' ', Camper.lastname_mother).label('Nombre del camper'),
                        MedicalCamperVisit.id,
                        MedicalCamperVisit.attention_date.label('Fecha de consulta'),
                        MedicalCamperVisit.attention_time.label('Hora de consulta'),
                        MedicalCamperVisit.diagnostic.label('Diagnostico'),
                        MedicalCamperVisit.doctor.label('Doctor que atendió'),
                        MedicalCamperVisit.description.label('Descripción de la lesión'),
                        Constant.value.label('triage'),
                        MedicalCamperVisit.medication_authorization.label('¿Quién autorizó el medicamento?'),
                        MedicalCamperVisit.event_description.label('Descripción del evento'),
                        MedicalCamperVisit.camp_restriction.label('Medidas durante el camp'),
                        MedicalCamperVisit.administered_medications.label('Tratamiento'),
                        MedicalCamperVisit.medical_monitoring.label('Seguimiento médico'),
                        MedicalCamperVisit.send_in_email.label('Notificar a los padres'),
                        MedicalCamperVisit.comment.label('Comentario'),
                        MedicalCamperVisit.initial_visit_id.label('medical_camper_visit'),
                        MedicalCamperVisit.medical_comment.label('Comentario interno'),
                        MedicalCamperVisit.additional_photo.label('Foto adicional')
                     
                     )
                      .select_from(MedicalCamperVisit)
                      .join(Camper, MedicalCamperVisit.camper_id == Camper.id)
                      .join(Constant, Constant.id == MedicalCamperVisit.triage)
                      .filter(MedicalCamperVisit.camp_id == camp_id)
             )
    medical_visits = db.execute(query)
    medical_visits = medical_visits.mappings().all()

    medical_visits_report = []
   
    for visit in medical_visits:
        
        visit_dict = dict(visit)
        
        visit_dict["Foto adicional"] = f"{BACKEND_DEV_URL}/{visit_dict['Foto adicional']}" if visit_dict['Foto adicional'] else ""
        
        visit_dict["Notificar a los padres"] = "Sí" if visit_dict['Notificar a los padres'] else "No"
        
        
        if visit.medical_camper_visit is not None:
            current_medical_visit = next(((medical_visit) for medical_visit in medical_visits if medical_visit.medical_camper_visit == visit.medical_camper_visit),None)
            visit_dict["Consulta de seguimiento"] = f"(seguimiento) - {current_medical_visit.Diagnostico}"
        else:
            visit_dict["Consulta de seguimiento"] = "Primera visita"
        medical_visits_report.append(visit_dict)                   
    
    return medical_visits_report


def get_camp_payments_report(db: Session, camp_id: int):
        
    camp_payments_query = (
        db.query(
            Payment.id.label("payment_id"),
            Payment.payment_amount,
            Payment.payment_date,
            Payment.txn_number.label("transaction"),
            Payment.txn_type_id,
            PaymentMethod.name.label("payment_method"),
            Currency.acronyms.label("currency_acronym"),
            Currency.symbol.label("currency_symbol"),
            func.concat(Camper.name, ' ', Camper.lastname_father, ' ', Camper.lastname_mother).label("camper_fullname"),
            Camper.id.label("camper_id"),     
        ).select_from(Payment)
        .join(PaymentMethod, Payment.payment_method_id == PaymentMethod.id)
        .join(Currency, Currency.id == Payment.currency_id)
        .join(Camper, Camper.id == Payment.camper_id)
        .filter(Payment.camp_id == camp_id)
        .order_by(Camper.name)
    )
    
    camp_payments = db.execute(camp_payments_query)
    camp_payments = camp_payments.mappings().all()
    
    payments_report = []
    for payment in camp_payments:
        payment_dict = dict(payment)
        
        payment_amount = "{:,.2f}".format(abs(payment.payment_amount))

        payment_dict["payment_amount"] = payment_amount
        payment_dict["charge"] = ""
        payment_dict["pay"] = ""
        payment_dict["discount"] = ""
        
        formated_amount = payment_dict["currency_symbol"] + payment_amount + " " + payment_dict["currency_acronym"]
        
        if payment_dict["txn_type_id"] in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID):
            if payment_dict["txn_type_id"] == TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID:
                payment_dict["discount"] = formated_amount
            else:
                payment_dict["pay"] = formated_amount        
        else:
            payment_dict["charge"] = formated_amount
        
        del payment_dict["currency_acronym"]
        del payment_dict["currency_symbol"]
        del payment_dict["txn_type_id"]
        del payment_dict["payment_id"]
        del payment_dict["payment_amount"]
        payments_report.append(payment_dict)

    return payments_report




def get_camp_gnl_staff_report(db: Session, camp_id: int):
    
    
    query = (db.query(Staff.id,
                      Staff.name,
                      Staff.lastname_father,
                      Staff.lastname_mother,
                      Constant.value.label('gender'),
                      User.email.label("email"),
                      Staff.curp,
                      Staff.rfc,
                      Staff.cellphone,
                      Staff.home_phone,
                      Staff.birthday,
                      Staff.affliction, 
                      Staff.blood_type,
                      Staff.drug_allergies,
                      Staff.other_allergies,
                      Staff.nocturnal_disorders,
                      Staff.phobias,
                      Staff.drugs,
                      Staff.prohibited_foods,
                      Staff.bio,
                      Staff.coordinator,
                      Staff.facebook,
                      Staff.staff_contact_name,
                      Staff.staff_contact_relation,
                      Staff.staff_contact_homephone,
                      Staff.staff_contact_cellphone,
                      ).select_from(StaffInCamp)
             .join(Staff, Staff.id == StaffInCamp.staff_id)
             .join(Constant, Constant.id == Staff.gender_id)
             .join(User, Staff.login_id == User.id)
             .filter(and_(StaffInCamp.camp_id == camp_id, StaffInCamp.confirmed_staff == True)))
    staffs = db.execute(query)
    staffs = staffs.mappings().all()
    
    
    staffs_report = []
   
    for staff in staffs:
        staff_dict = dict(staff)

        staff_vaccines = get_staff_all_vaccines_by_staff_id(db, staff.id)
        staff_food_restriction = get_all_staff_food_restriction_by_id(db, staff.id)
        
        for food_restriction in staff_food_restriction:
            print(food_restriction)
            staff_dict[food_restriction["name"]] = food_restriction["is_active"]
        
        for vaccine in staff_vaccines:
            staff_dict[vaccine["name"]] = vaccine["is_active"]
            
        staffs_report.append(staff_dict)
       
    return staffs_report


def get_all_camp(db: Session, pagination: Pagination):
    order = desc if pagination.order == SortEnum.DESC else asc

    query = (
        db.query(
            Camp.id,
            Camp.name,
            Camp.start,
            Camp.end,
            Camp.start_registration,
            Camp.end_registration,
            Camp.registration,
            Camp.url,
            Camp.special_message,
            Camp.special_message_admin,
            Camp.public_price,
            Camp.show_payment_parent,
            Camp.show_rebate_parent,
            Camp.show_paypal_button,
            Camp.show_payment_order,
            Camp.reminder_camp_days,
            Camp.reminder_discount_days,                                                        
            Camp.insurance,
            Camp.venue,
            Camp.photo_url,
            Camp.photo_password,
            Camp.medical_report,
            Camp.occupancy_camp,
            Camp.active,
            Camp.general_camp,
            Camp.show_mercadopago_button,
            Camp.recommended_payment_dates
        ).select_from(Camp)
        .order_by(order(Camp.name))
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = db.query(func.count(Camp.id)).select_from(Camp).scalar()    
    pages = get_number_of_pages(rows_count, pagination.perPage)

    return  {
        "pages": pages,
        "items": data,
        "total": rows_count
    }
    
    

    

def get_all_active_camp(db: Session, pagination):
    camps = []
    order = desc if pagination.order == SortEnum.DESC else asc
    
    query = (select(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.public_price.label("camp_public_price"),
            Camp.show_payment_parent.label("camp_show_payment_parent"),
            Camp.active,
            Location.name.label("location_name"),
            School.name.label("school_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Currency.name.label("camp_currency_name"),
            Currency.symbol.label("camp_currency_symbol"),
            Currency.acronyms.label("camp_currency_acronym"),
            Camp.photo_password
        
        )
        .join(Location, Location.id == Camp.location_id)
        .join(School, School.id == Camp.school_id)
        .join(Currency, Currency.id == Camp.currency_id)
        .order_by(order(Camp.created_at))
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = db.query(func.count(Camp.id)).select_from(Camp).join(Location, Location.id == Camp.location_id).join(Currency, Currency.id == Camp.currency_id).scalar()    
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    for row in data:
        records = get_records_for_camp(db, row.camp_id)
        row = dict(row)
        row["records"] = records
        camps.append(row)

    return {
        "pages": pages,
        "items": camps,
        "total": rows_count
    }
    
def get_forthcomming_active_camp(db: Session, pagination):
    camps = []
    order = desc if pagination.order == SortEnum.DESC else asc
    
    query = (select(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.public_price.label("camp_public_price"),
            Camp.show_payment_parent.label("camp_show_payment_parent"),
            Camp.active,
            Location.name.label("location_name"),
            School.name.label("school_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Currency.name.label("camp_currency_name"),
            Currency.symbol.label("camp_currency_symbol"),
            Currency.acronyms.label("camp_currency_acronym"),
            Camp.photo_password
        
        )
        .join(Location, Location.id == Camp.location_id)
        .join(School, School.id == Camp.school_id)
        .join(Currency, Currency.id == Camp.currency_id)
        .filter(Camp.start >= date.today())
        .order_by(order(Camp.created_at))
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = db.query(func.count(Camp.id)).select_from(Camp).join(Location, Location.id == Camp.location_id).join(Currency, Currency.id == Camp.currency_id).filter(Camp.start >= date.today()).scalar()    
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    for row in data:
        records = get_records_for_camp(db, row.camp_id)
        row = dict(row)
        row["records"] = records
        camps.append(row)

    return {
        "pages": pages,
        "items": camps,
        "total": rows_count
    }




def search_all_active_camp(db: Session, pagination, name, location, school):
    order = desc if pagination.order == SortEnum.DESC else asc
    camps = []
    db.execute(text('SET pg_trgm.similarity_threshold = 0.2'))
    query = (select(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.public_price.label("camp_public_price"),
            Camp.show_payment_parent.label("camp_show_payment_parent"),
            Camp.active,
            Location.name.label("location_name"),
            School.name.label("school_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Currency.name.label("camp_currency_name"),
            Currency.symbol.label("camp_currency_symbol"),
            Currency.acronyms.label("camp_currency_acronym"),
            Camp.photo_password
        )
        .join(Location, Location.id == Camp.location_id)
        .join(School, School.id == Camp.school_id)
        .join(Currency, Currency.id == Camp.currency_id)
        .filter(
            or_(
                Camp.name.op('%')(name),
                School.name.op('%')(school),
                Location.name.op('%')(location),
        ))
        .order_by(        
            func.similarity(Camp.name, name).desc(),
            func.similarity(School.name, school).desc(),
            func.similarity(Location.name, location).desc()
        )
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = (
        db.query(func.count(Camp.id)).select_from(Camp).join(Location, Location.id == Camp.location_id).join(School, School.id == Camp.school_id).join(Currency, Currency.id == Camp.currency_id)
        .filter(
            or_(
                Camp.name.op('%')(name),
                School.name.op('%')(school),
                Location.name.op('%')(location),
        )).scalar()
        )    
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    for row in data:
        records = get_records_for_camp(db, row.camp_id)
        row = dict(row)
        row["records"] = records
        camps.append(row)

    return {
        "pages": pages,
        "items": camps,
        "total": rows_count
    }



def get_school_camp_for_camper(db: Session, camper_id: int):
    school_id = db.query(Camper.school_id).filter_by(id=camper_id).first()
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            Camp.registration
        )
        .join(Location, Location.id == Camp.location_id)
        .filter(
            and_(
                Camp.general_camp == False,
                Camp.school_id == school_id[0],
                Camp.active == True,
                Camp.start >= date.today()
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)


def get_summer_camp_for_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            Camp.registration
        )
        .join(Location, Location.id == Camp.location_id)
        .filter(
            and_(
                Camp.general_camp == True,
                Camp.active == True,
                Camp.start >= date.today()
            )
        )
    )
    return db_mapping_rows_to_dict(rows)


def get_camp_by_id(db: Session, camp_id: int):
    return db.query(Camp).filter_by(id=camp_id).first()


def get_camp_staff_by_camp_id(db: Session, camp_id: int):
    query = db.query( Camp.id,
                     Camp.name,
                     Camp.start,
                     Camp.end,
                     Camp.start_registration,
                     Camp.end_registration,
                     Camp.registration,
                     Camp.url,
                     Camp.special_message,
                     Camp.special_message_admin,
                     Camp.public_price,
                     Camp.show_payment_parent,
                     Camp.show_rebate_parent,
                     Camp.show_paypal_button,
                     Camp.show_payment_order,
                     Camp.reminder_camp_days,
                     Camp.reminder_discount_days,                                                        
                     Camp.insurance,
                     Camp.venue,
                     Camp.photo_url,
                     Camp.photo_password,
                     Camp.medical_report,
                     Camp.occupancy_camp,
                     Camp.active,
                     Camp.general_camp,
                     Camp.location_id,
                     Camp.school_id,
                     Currency.name.label("camp_currency_name"),
                     Currency.symbol.label("camp_currency_symbol"),
                     Currency.acronyms.label("camp_currency_acronyms"),
                     Camp.recommended_payment_dates,
                     Camp.show_mercadopago_button,
                     Camp.created_at,
                     Camp.updated_at
                     ).select_from(Camp).join(Currency, Currency.id == Camp.currency_id).filter(Camp.id == camp_id)
    
    data = db.execute(query)
    data = data.mappings().first()
    return data


def create_new_camp(db: Session, new_camp: CampCreate):
    db_camp = None
    try:
        db_camp = Camp(**new_camp.dict())
        db.add(db_camp)
        db.commit()
        db.refresh(db_camp)
    except SQLAlchemyError as e:
        print("#========================#")
        print(e)
        print("#========================#")
        db_camp = None
        return db_camp
    except Exception as ex:
        print(f"No se pudo guardar en la base de datos: {ex}")
    return db_camp


# def update_camp_by_id(db: Session, camp_id: int, modify_camp: CampModify):
#     rows_updated = (
#         db.query(Camp)
#         .filter_by(id=camp_id)
#         .update(modify_camp, synchronize_session="fetch")
#     )
#     db.commit()
#     return rows_updated

def update_camp_by_id(db: Session, camp_id: int, modify_camp):
    
    try:
        extra_charges = [extra_charge.dict(exclude_unset=True) for extra_charge in modify_camp.extra_charges]
        extra_questions = [extra_question.dict(exclude_unset=True) for extra_question in modify_camp.extra_question]
        camp_payment_accounts = [camp_payment_account.dict(exclude_unset=True) for camp_payment_account in modify_camp.payment_accounts]
        
        
        campers_in_camp = (db.query(CamperInCamp, Camper, Camp)
                .select_from(CamperInCamp)
                .join(Camper, Camper.id == CamperInCamp.camper_id)
                .join(Camp, Camp.id == CamperInCamp.camp_id)
                .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID)).all())
        
        current_camp_extra_charges_query = (db.query(CampExtraCharge.camp_id, 
                                                     CampExtraCharge.id,
                                                     CampExtraCharge.name,
                                                     CampExtraCharge.price,
                                                     CampExtraCharge.currency_id,
                                                    #  CampExtraCharge.created_at,
                                                    #  CampExtraCharge.updated_at
                                                     ).select_from(CampExtraCharge).filter(CampExtraCharge.camp_id == camp_id))
        current_camp_extra_charges = db.execute(current_camp_extra_charges_query)
        current_camp_extra_charges = current_camp_extra_charges.mappings().all()
        
        current_camp_extra_questions_query = (db.query(CampExtraQuestion.id,
                                                       CampExtraQuestion.camp_id,
                                                       CampExtraQuestion.is_required,
                                                       CampExtraQuestion.question)
                                              .select_from(CampExtraQuestion).filter(CampExtraQuestion.camp_id == camp_id))
        current_camp_extra_questions = db.execute(current_camp_extra_questions_query)
        current_camp_extra_questions = current_camp_extra_questions.mappings().all()
        
        current_camp_payment_accounts_query = (
            db.query(CampPaymentAccount.id, CampPaymentAccount.camp_id, CampPaymentAccount.paymentaccount_id)
            .select_from(CampPaymentAccount)
            .filter(CampPaymentAccount.camp_id == camp_id)
        )
        current_camp_payment_accounts = db.execute(current_camp_payment_accounts_query)
        current_camp_payment_accounts = current_camp_payment_accounts.mappings().all()
        
        ids_payment_accounts = set()        
        for item in current_camp_payment_accounts:
                ids_payment_accounts.add(item["paymentaccount_id"])
        camp_payment_accounts_to_add = [item for item in camp_payment_accounts if item["id"] not in ids_payment_accounts] 
        
        ids_current_camp_payment_accounts = set()
        for item in camp_payment_accounts:
            if "id" in item:
                ids_current_camp_payment_accounts.add(item["id"])
        camp_payment_accounts_to_be_deleted = [item for item in current_camp_payment_accounts if item["paymentaccount_id"] not in ids_current_camp_payment_accounts]
        
        
         # delete camp payment accounts       
        for camp_payment_account_to_be_deleted in camp_payment_accounts_to_be_deleted:
            camp_payment_account_deleted = (db.query(CampPaymentAccount).filter(CampPaymentAccount.paymentaccount_id == camp_payment_account_to_be_deleted["paymentaccount_id"]).delete(synchronize_session = 'fetch'))
        
         # add camp payment accounts       
        for camp_payment_account_to_be_added in camp_payment_accounts_to_add:
            camp_payment_account_added = CampPaymentAccount(
                camp_id=camp_id,
                paymentaccount_id=camp_payment_account_to_be_added["id"]
            )
            db.add(camp_payment_account_added)
        
        
        
        
        ids_current_extra_question = set()        
        for item in extra_questions:
            if "id" in item:
                ids_current_extra_question.add(item["id"])        
        camp_extra_questions_to_be_deleted = [item for item in current_camp_extra_questions if item["id"] not in ids_current_extra_question]


        ids_a = set()        
        for item in extra_charges:
            if "id" in item:
                ids_a.add(item["id"])        
        camp_extra_charges_to_be_deleted = [item for item in current_camp_extra_charges if item["id"] not in ids_a]
                
        # delete extra charges        
        for camp_extra_charge_to_be_deleted in camp_extra_charges_to_be_deleted:
            
            
            for camper_in_camp in campers_in_camp:
                camper_extra_charge_is_selected = (db.query(CamperExtraCharge.payment_id)
                                                .select_from(CamperExtraCharge)
                                                .filter(and_(CamperExtraCharge.camper_id == camper_in_camp[1].id, CamperExtraCharge.extra_charge_id == camp_extra_charge_to_be_deleted["id"])).first())
                
                if camper_extra_charge_is_selected.payment_id is not None:
                    
                    canceled_camper_extra_charge = {
                        "paid": False,
                        "payment_amount": camp_extra_charge_to_be_deleted.price,
                        "txn_number": "Cancelación de cargo extra" + " " + camp_extra_charge_to_be_deleted.name,
                        "camp_id": camp_id,
                        "payment_date": datetime.now(),
                        "camper_id": camper_in_camp[1].id,
                        "currency_id": camper_in_camp[2].currency_id,
                        "parent_id": camper_in_camp[1].parent_id,
                        "txn_type_id": TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID
                }

                    create_new_payment_and_update_balance_transaction(db, canceled_camper_extra_charge)
            
            camp_extra_charge_deleted = (db.query(CampExtraCharge).filter(CampExtraCharge.id == camp_extra_charge_to_be_deleted["id"]).delete(synchronize_session='fetch'))

        
        
        for extra_charge in extra_charges:
            
            if not "id" in extra_charge:
                extra_charge['camp_id'] = camp_id
                db_extra_charge = CampExtraCharge(**extra_charge)
                db.add(db_extra_charge) 
                db.flush()
                for camper_in_camp in campers_in_camp:
                    new_camper_extra_charge = CamperExtraCharge(**{"camper_id": camper_in_camp[1].id, "extra_charge_id": db_extra_charge.id, "is_selected": False, "payment_id": None})
                    db.add(new_camper_extra_charge)
                    

            else:            
                current_extra_charge = db.query(CampExtraCharge).filter(CampExtraCharge.id == extra_charge['id']).first()

                if current_extra_charge.price != extra_charge['price']:
                    db.query(CampExtraCharge).filter(CampExtraCharge.id == extra_charge['id']).update(
                    extra_charge, synchronize_session="fetch")
                    for camper_in_camp in campers_in_camp:
                        camper_extra_charge = (db.query(CamperExtraCharge)
                                                    .select_from(CamperExtraCharge)
                                                    .filter(and_(CamperExtraCharge.camper_id == camper_in_camp[1].id, CamperExtraCharge.extra_charge_id == extra_charge['id']))
                                                    .first()
                                                )
                        if camper_extra_charge.payment_id is not None:
                            delete_payment_and_update_balance_transaction(db, camper_extra_charge.payment_id, camper_in_camp[1].id)
                        
                        payment_extra_charge = {
                            "paid": False,
                            "payment_amount": extra_charge['price'],
                            "txn_number": "Costo extra" + " " + extra_charge['name'],
                            "camp_id": extra_charge['camp_id'],
                            "payment_date": datetime.now(),
                            "camper_id": camper_in_camp[1].id,
                            "currency_id": camper_in_camp[2].currency_id,
                            "parent_id": camper_in_camp[1].parent_id,
                            "txn_type_id": TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID
                                
                        }
                        extra_charge_new_payment = create_new_payment_and_update_balance_transaction(db, payment_extra_charge)
                        camper_extra_charge.payment_id = extra_charge_new_payment.id
                else:
                    db.query(CampExtraCharge).filter(CampExtraCharge.id == extra_charge['id']).update(
                    extra_charge,synchronize_session="fetch")
        
        
        
        for camp_extra_question_to_be_deleted in camp_extra_questions_to_be_deleted:
            camp_extra_question_deleted = (db.query(CampExtraQuestion).filter(CampExtraQuestion.id == camp_extra_question_to_be_deleted["id"]).delete(synchronize_session='fetch'))
        
        
        for extra_question in extra_questions:

            
            if not "id" in extra_question:
                extra_question['camp_id'] = camp_id
                new_extra_question = CampExtraQuestion(**extra_question)
                db.add(new_extra_question) 
                db.flush()
                for camper_in_camp in campers_in_camp:
                    new_camper_extra_question = CamperExtraAnswer(**{"camper_id": camper_in_camp[1].id, "question_id": new_extra_question.id, "answer":""})
                    db.add(new_camper_extra_question)
            else:
                updated_extra_question = db.query(CampExtraQuestion).filter(CampExtraQuestion.id == extra_question['id']).update(
                    extra_question, synchronize_session="fetch")

        updated_camp= (
            db.query(Camp)
            .filter_by(id=camp_id)
            .update(modify_camp.camp.dict(exclude_unset=True), synchronize_session="fetch")
        )
        db.commit()
        
        
        return 1

    
    except Exception as ex:
        db.rollback()
        print(f"An error occurred: {type(ex).__name__} – {ex}")
        traceback.print_exc()
        return 3


def delete_camp(db: Session, camp_id: int):
    camp = db.query(Camp).filter(Camp.id == camp_id).first()
    db.delete(camp)
    db.commit()
    return {"status": True}


def get_records_for_camp(db: Session, camp_id: int):
    campers_record = get_campers_for_module_count(db, camp_id)
    staff_available_record = get_staff_volunteer_in_camp_count(db, camp_id)
    staff_record = get_staff_in_camp_count(db, camp_id)

    return {
        "campers_recod": campers_record,
        "staff_available_record": staff_available_record,
        "staff_record": staff_record,
    }


# 2


def get_camp_by_search(db: Session, search: str):
    camps = (
        db.query(Camp.id.label("camp_id"), Camp.name.label("camp_name"))
        .filter(Camp.name.ilike(r"%{}%".format(search)))
        .all()
    )

    if not camps:
        return "Data not found"

    return db_mapping_rows_to_dict(camps)


def get_camp_by_search(db: Session, search: str):
    camps = (
        db.query(Camp.id.label("camp_id"), Camp.name.label("camp_name"))
        .filter(Camp.name.ilike(r"%{}%".format(search)))
        .all()
    )

    if not camps:
        return "Data not found"

    return db_mapping_rows_to_dict(camps)

def get_school_info_by_camp(db: Session, camp_id:int):
    query = (db.query(School.id.label('school_id'), School.name, School.email, School.contact_second_email, School.contact_third_email )
             .join(Camp, Camp.school_id == School.id).filter(Camp.id == camp_id)
             )
    data = db.execute(query)
    return data.mappings().first()

def create_new_camp_payment_account(db: Session, new_camp_payment_account):
    db_camp_payment_account = None
    try:
        db_camp_payment_account = CampPaymentAccount(**new_camp_payment_account.dict())
        db.add(db_camp_payment_account)
        db.commit()
        db.refresh(db_camp_payment_account)
    except SQLAlchemyError as e:
        db.rollback()
        print("#========================#")
        print(e)
        print("#========================#")
        db_camp_payment_account = None
        return db_camp_payment_account
    except Exception as ex:
        db.rollback()
        print(f"No se pudo guardar en la base de datos: {ex}")
    return db_camp_payment_account

def create_camp_camper_paypal_link(db: Session, camp_id: int, camper_id: int ):
    camper_in_camp = (db.query(CamperInCamp)
                        .select_from(CamperInCamp)
                        .filter(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id)
                        .first()
    )
    amount_to_pay = f"{camper_in_camp.payment_balance * 1.05:.2f}"
      
    paypal_link = f"{PAYPAL_LINK_URL}/{amount_to_pay}"
    
    return {"data": paypal_link}