import os
from collections import defaultdict
from sqlalchemy import case, distinct, and_
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased
from utils.db import db_mapping_rows_to_dict
from datetime import date, datetime
from model.groupings.grouping import Grouping
from model.groupings.grouping_camp import GroupingCamp
from model.groupings.grouping_camper import GroupingCamper
from model.groupings.grouping_type import GroupingType
from model.camps import CamperInCamp, Camp, Location, CampExtraCharge, CampExtraQuestion
from model.campers import Camper, CamperRecord, Parent, School, CamperExtraAnswer
from model.payments import CamperExtraCharge, Payment
from model.catalogs import Constant, Currency
from model.user import User
from schema.camps.camper_in_camp_schema import (
    CamperInCampCreate,
    CamperInCampModify,
)

from schema.campers.camper_extra_answer_schema import (
    CamperExtraAnswerCreate,
    ExtraAnswerMultiple,
)
from schema.payments.camper_extra_charge_schema import (
    ExtraChargeMultiple,
    CamperExtraChargeCreate,
)
from schema.payments.payment_schema import PaymentCreate

from crud.campers.camper_extra_answer_crud import create_new_extra_answer, get_extra_answer_by_uuid, create_new_extra_answer_transaction
from crud.payments.camper_extra_charge_crud import create_new_camper_extra_charge, get_camper_extra_charge_by_id, create_new_camper_extra_charge_transaction, create_new_payment_and_update_balance_transaction
from crud.campers.camper_comment_crud import get_camper_comment_by_camper_for_admin
from crud.camps.camp_extra_charge_crud import get_extra_charge_by_id, get_extra_charge_by_camp
from crud.campers.parent_crud import get_parent_by_camper_id, get_second_tutor_by_camper_id
from crud.campers.camper_crud import get_camper_by_uuid
from crud.campers.camper_extra_answer_crud import get_extra_answer_by_camper_camp
from crud.camps.camp_extra_question_crud import get_extra_question_by_camp
from crud.mailings.mailing_crud import get_admin_users_for_mailing, get_camper_info_mailing, get_camp_info_by_id_mailing
from crud.payments.payment_crud import get_camper_payments_in_camp
from helper.camper_helpers import update_record_campers
from helper.mailing_helpers import send_mail_template
from utils.payments.payment_table import get_payment_table, create_payment_table_unformatted

from crud.payments.payment_crud import get_payment_transaction_type_by_movement, create_new_payment_and_update_balance, create_new_payment, create_new_payment_transaction, delete_payment_and_update_balance

CAMP_STATUS_ENROLLED_ID = int(os.getenv("CAMP_STATUS_ENROLLED_ID"))
CAMP_STATUS_CANCELLED_ID = int(os.getenv("CAMP_STATUS_CANCELLED_ID"))
TRANSACTION_TYPE_CAMP_PRICE_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PRICE_ID"))
TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID"))
CAMP_REGISTRATION_PARENT_TEMPLATE_ID = int(os.getenv("CAMP_REGISTRATION_PARENT_TEMPLATE_ID"))
CAMP_REGISTRATION_STAFF_TEMPLATE_ID = int(os.getenv("CAMP_REGISTRATION_STAFF_TEMPLATE_ID"))


def get_all_camper_in_camp(db: Session):
    rows = db.query(CamperInCamp).all()
    return rows


def create_new_camper_in_camp(db: Session, new_camper_in_camp: CamperInCampCreate):
    db_camper_in_camp = None
    try:
        camp_price = (
            db.query(Camp.public_price).filter_by(id=new_camper_in_camp.camp_id).first()
        )
        db_camper_in_camp = CamperInCamp(
            camp_id=new_camper_in_camp.camp_id,
            status=new_camper_in_camp.status,
            payment_balance=getattr(camp_price, "public_price"),
            camper_id=new_camper_in_camp.camper_id,
        )
        db.add(db_camper_in_camp)
        db.commit()
        db.refresh(db_camper_in_camp)
    except SQLAlchemyError as e:
        print("#=================")
        print(e)
        print("#=================")
        db_camper_in_camp = None
        return db_camper_in_camp
    except Exception as ex:
        print(f"No se pudo guardar en la base de datos: {ex}")
    return db_camper_in_camp


def create_new_camper_in_camp_transaction(db: Session, new_camper_in_camp: CamperInCampCreate):
    camp_price = (
        db.query(Camp.public_price).filter_by(id=new_camper_in_camp.camp_id).first()
    )
    db_camper_in_camp = CamperInCamp(
        camp_id=new_camper_in_camp.camp_id,
        status=new_camper_in_camp.status,
        payment_balance=getattr(camp_price, "public_price"),
        camper_id=new_camper_in_camp.camper_id,
    )
    db.add(db_camper_in_camp)
    db.flush()
    return db_camper_in_camp


def update_camper_in_camp_by_id(
    db: Session,
    camp_id: int,
    camper_id: int,
    modify_camper_in_camp: CamperInCampModify,
):
    print("######################################################")
    print(type(modify_camper_in_camp))
    rows_updated = (
        db.query(CamperInCamp)
        .filter(
            and_(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id)
        )
        .update(modify_camper_in_camp, synchronize_session="fetch")
    )
    print(rows_updated)
    db.commit()
    return rows_updated


def get_subscribe_by_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camper.id.label("camper_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Camp.show_payment_parent,
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            Camp.show_payment_parent,
            CamperInCamp.payment_balance.label("camper_payment_balance"),
            Currency.symbol.label("currency_symbol"),
            Currency.acronyms.label("currency_acronyms"),
        )
        .join(Camp, CamperInCamp.camp_id == Camp.id)
        .outerjoin(Currency, Currency.id == Camp.currency_id)
        .join(Camper, CamperInCamp.camper_id == Camper.id)
        .join(Constant, CamperInCamp.status == Constant.id)
        .join(Location, Camp.location_id == Location.id)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.status == CAMP_STATUS_ENROLLED_ID,
                Camp.active == True,
                Camp.start >= date.today(),
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)


def get_cancelled_by_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Location.name.label("location_name"),
            Camp.show_payment_parent,
            Camp.public_price.label("public_price"),
            CamperInCamp.payment_balance.label("camper_payment_balance"),
            Currency.symbol.label("currency_symbol"),
            Currency.acronyms.label("currency_acronyms"),
        )
        .join(Camp, CamperInCamp.camp_id == Camp.id)
        .outerjoin(Currency, Currency.id == Camp.currency_id)
        .join(Constant, CamperInCamp.status == Constant.id)
        .join(Location, Camp.location_id == Location.id)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.status == CAMP_STATUS_CANCELLED_ID,
                Camp.active == True,
                Camp.start >= date.today(),
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)


def get_all_cancelled_by_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            CamperInCamp.payment_balance.label("camper_payment_balance"),
        )
        .join(Camp, CamperInCamp.camp_id == Camp.id)
        .join(Constant, CamperInCamp.status == Constant.id)
        .join(Location, Camp.location_id == Location.id)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.status == CAMP_STATUS_CANCELLED_ID,
                Camp.active == True,
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)


def get_past_subscribe_by_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Camp.show_payment_parent,
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            CamperInCamp.payment_balance.label("camper_payment_balance"),
            Currency.symbol.label("currency_symbol"),
            Currency.acronyms.label("currency_acronyms"),
            
        )
        .join(Camp, CamperInCamp.camp_id == Camp.id)
        .join(Constant, CamperInCamp.status == Constant.id)
        .outerjoin(Currency, Currency.id == Camp.currency_id)
        .join(Location, Camp.location_id == Location.id)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.status == CAMP_STATUS_ENROLLED_ID,
                Camp.active == True,
                Camp.start < date.today(),
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)

def get_past_due_camps_by_camper(db: Session, camper_id: int):
    rows = (
        db.query(
            Camp.id.label("camp_id"),
            Camp.name.label("camp_name"),
            Camp.start.label("camp_start"),
            Camp.end.label("camp_end"),
            Camp.show_payment_parent,
            Location.name.label("location_name"),
            Camp.public_price.label("public_price"),
            CamperInCamp.payment_balance.label("camper_payment_balance"),
            Currency.symbol.label("currency_symbol"),
            Currency.acronyms.label('currency_acronyms')
        )
        .join(Camp, CamperInCamp.camp_id == Camp.id)
        .outerjoin(Currency, Currency.id == Camp.currency_id)
        .join(Constant, CamperInCamp.status == Constant.id)
        .join(Location, Camp.location_id == Location.id)
        .filter(
            and_(
                CamperInCamp.camper_id == camper_id,
                CamperInCamp.status == CAMP_STATUS_ENROLLED_ID,
                Camp.active == True,
                Camp.start < date.today(),
                CamperInCamp.payment_balance >= 0   
            )
        )
        .all()
    )
    return db_mapping_rows_to_dict(rows)


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


def get_campers_for_module(db: Session, camp_id: int):
    campers = (
        db.query(
            Camper.id.label("camper_id"),
            Camper.name.label("camper_name"),
            Camper.lastname_father.label("camper_lastname_father"),
            Camper.lastname_mother.label("camper_lastname_mother"),
        )
        .join(CamperInCamp, CamperInCamp.camper_id == Camper.id)
        .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID))
        .all()
    )
    return db_mapping_rows_to_dict(campers)

def get_campers_for_module_count(db: Session, camp_id: int):
    campers = (
        db.query(
            CamperInCamp.id
        )
        .select_from(CamperInCamp)
        .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID))
        .count()
    )
    return campers

def get_camps_name_amount_camper(db: Session, camper_id: int):
    data = []
    camps = get_subscribe_by_camper(db, camper_id)
    # cancelled_camps = get_all_cancelled_by_camper(db, camper_id)

    for camp in camps:
        data.append(
            {
                "camp_id": getattr(camp, "camp_id"),
                "camp_name": getattr(camp, "camp_name"),
                "camper_payment_balance": getattr(camp, "camper_payment_balance"),
                "currency_symbol": getattr(camp, "currency_symbol"),
                "currency_acronyms": getattr(camp, "currency_acronyms"),
                "show_payment_parent": getattr(camp, "show_payment_parent")
            }
        )
    """
    for camp in cancelled_camps:
        if getattr(camp, "camper_payment_balance") > 0:
            data.append(
                {
                    "camp_id": getattr(camp, "camp_id"),
                    "camp_name": getattr(camp, "camp_name"),
                    "camper_payment_balance": getattr(camp, "camper_payment_balance"),
                }
            )
    """
    return data


def get_campers_for_camp(db: Session, camp_id: int):
    campers = (
        db.query(
            CamperInCamp.id.label("camper_in_camp_id"),
            Camper.record_id.label("camper_record_id"),
            CamperRecord.id.label("record_id"),
            Camper.id.label("camper_id"),
            Camper.photo.label("camper_photo"),
            Camper.doctor_precall.label("camper_doctor_precall"),
            (
                Camper.name
                + " "
                + Camper.lastname_father
                + " "
                + Camper.lastname_mother
            ).label("camper_full_name"),
            CamperRecord.attend.label("camper_attend"),
            CamperRecord.attended.label("camper_attended"),
            CamperRecord.total.label("camper_total"),
            CamperInCamp.payment_balance.label("camper_total_balance"),
            Camper.birthday.label("camper_birthday"),
            (
                Parent.tutor_name
                + " "
                + Parent.tutor_lastname_father
                + " "
                + Parent.tutor_lastname_mother
            ).label("tutor_full_name"),
            Parent.id.label("parent_id"),
            User.email.label("tutor_email"),
            (
                Parent.contact_name
                + " "
                + Parent.contact_lastname_father
                + " "
                + Parent.contact_lastname_mother
            ).label("second_tutor_full_name"),
            Parent.contact_email.label("second_tutor_email"),
        )
        .join(Camper, CamperInCamp.camper_id == Camper.id)
        .join(Parent, Camper.parent_id == Parent.id)
        .join(CamperRecord, Camper.record_id == CamperRecord.id)
        .join(User, Parent.user_id == User.id)
        .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID))
        .all()
    )
    campers_complete = []
     
    for camper in db_mapping_rows_to_dict(campers):
        camper_payments_in_camp =  get_camper_payments_in_camp(db, camper.camper_id, camp_id)
        payment_table = create_payment_table_unformatted(db, camper_payments_in_camp)  
         
        balance = 0
        if len(payment_table) > 0:
            balance = payment_table[-1]["balance"]
        
        comments = get_camper_comment_by_camper_for_admin(db, camper.camper_id)
        
        
        campers_complete.append(
            {
                "camper_in_camp_id": camper.camper_in_camp_id,
                "camper_record_id": camper.camper_record_id,
                "record_id": camper.record_id,
                "camper_id": camper.camper_id,
                "camper_photo": camper.camper_photo,
                "camper_full_name": camper.camper_full_name,
                "camper_comments": len(comments),
                "camper_doctor_precall": camper.camper_doctor_precall,
                "camper_attend": camper.camper_attend,
                "camper_attended": camper.camper_attended,
                "camper_total": camper.camper_total,
                "camper_total_balance": balance,
                "camper_birthday": camper.camper_birthday,
                "tutor_full_name": camper.tutor_full_name,
                "tutor_email": camper.tutor_email,
                "parent_id": camper.parent_id,
                "second_tutor_full_name": camper.second_tutor_full_name,
                "second_tutor_email": camper.second_tutor_email,
            }
        )   

    return campers_complete


def get_campers_in_camp_mailing(db, camp_id):
        
    query = (
        db.query(
            Camper.id,
            (Camper.name + ' ' + Camper.lastname_father + ' ' + Camper.lastname_mother).label('camper_full_name'),
            (Parent.tutor_name + ' ' + Parent.tutor_lastname_father + ' ' + Parent.tutor_lastname_mother).label('tutor_full_name'),
            (Parent.contact_name + ' ' + Parent.contact_lastname_father + ' ' + Parent.contact_lastname_mother).label('second_tutor_full_name'),
            Parent.contact_email.label('second_tutor_email'),
            User.email.label('tutor_email')
        )
        .join(CamperInCamp, CamperInCamp.camper_id == Camper.id)
        .join(Parent, Parent.id == Camper.parent_id)
        .join(User, User.id == Parent.user_id)
        .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID))
    )
    
    data = db.execute(query)
    return data.mappings().all()

def get_campers_for_bracelets(db, camp_id):
    campers_query = (
        db.query(
            Camper.id.label("camper_id"),
            (
                Camper.name
                + " "
                + Camper.lastname_father
                + " "
                + Camper.lastname_mother
            ).label("name"),
            School.name.label("school"),
            Constant.value.label("blood_type"),
            Camper.drug_allergies.label("alergies"),
            Camper.other_allergies.label("other_alergies"),
            Camper.prohibited_foods,
        )
        .select_from(CamperInCamp)
        .join(Camper, Camper.id == CamperInCamp.camper_id)
        .join(School, School.id == Camper.school_id)
        .join(Constant, Constant.id == Camper.blood_type)
        .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.status == CAMP_STATUS_ENROLLED_ID))
        .order_by(Camper.lastname_father.asc())
    )
    campers = db.execute(campers_query)
    campers = campers.mappings().all()
    
    campers_list = []
    camp_grouping_types_query = (
        db.query(GroupingType.id, GroupingType.name).select_from(GroupingType)
        .join(Grouping, Grouping.grouping_type_id == GroupingType.id)
        .join(GroupingCamp, GroupingCamp.grouping_id == Grouping.id)
        .filter(GroupingCamp.camp_id == camp_id)
        .order_by(GroupingType.id)
        .distinct()
    )
    camp_grouping_types = db.execute(camp_grouping_types_query)
    camp_grouping_types = camp_grouping_types.mappings().all()
    
    
    for camper in campers:
        camper_dict = dict(camper)
        grouping_camper_query = (
            db.query(
                GroupingType.id.label("grouping_type_id"),
                Grouping.name
            ).select_from(GroupingCamper)
            .join(GroupingCamp, GroupingCamper.grouping_camp_id == GroupingCamp.id)
            .join(Grouping, Grouping.id == GroupingCamp.grouping_id)
            .join(GroupingType, GroupingType.id == Grouping.grouping_type_id)
            .filter(and_(GroupingCamper.camper_id == camper.camper_id, GroupingCamp.camp_id == camp_id))
        )
        grouping_camper = db.execute(grouping_camper_query)
        grouping_camper = grouping_camper.mappings().all()
        
        type_lookup = {t["id"]: t["name"] for t in camp_grouping_types}

        grouped = defaultdict(list)
        for g in grouping_camper:
            type_name = type_lookup.get(g["grouping_type_id"])
            if type_name:
                grouped[type_name].append(g["name"])
                
        camper_groupings = [{"name": (type_name, names)} for type_name, names in grouped.items()]
        camper_dict['groupings'] = camper_groupings
        campers_list.append(camper_dict)
        
    return campers_list




def subscribe_camper_to_camps(db, camps_id: list[int], camper_id: int):
    try:
        extra_charges = []

        prev_camper_in_camp = get_camper_in_camp_by_camper(db, camper_id)
        camper = get_camper_by_uuid(db, camper_id)
        camper_data_mailing = get_camper_info_mailing(db, camper_id)
        second_parent = get_second_tutor_by_camper_id(db, camper_id)
        parent = get_parent_by_camper_id(db, camper_id)
        admin_users = get_admin_users_for_mailing(db)
        for camp_id in camps_id:
            camp_data_mailing = get_camp_info_by_id_mailing(db, camp_id)
            camper_in_camp = (
                db.query(CamperInCamp)
                .filter(
                    and_(
                        CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id
                    )
                )
                .first()
            )
            # remove cancelled camp
            if camper_in_camp:  
                camper_extra_answers = (
                    db.query(CamperExtraAnswer).join(CampExtraQuestion, CamperExtraAnswer.question_id == CampExtraQuestion.id)
                    .where(and_(CamperExtraAnswer.camper_id == camper_id, 
                            CampExtraQuestion.camp_id == camp_id)).all())
                if camper_extra_answers:
                    for camper_extra_answer in camper_extra_answers:
                        camper_extra_answer_to_delete = db.query(CamperExtraAnswer).filter(CamperExtraAnswer.id == camper_extra_answer.id).first()
                        db.delete(camper_extra_answer_to_delete)
                camper_extra_charges = (
                    db.query(CamperExtraCharge).join(CampExtraCharge, CamperExtraCharge.extra_charge_id == CampExtraCharge.id)
                    .where(and_(CamperExtraCharge.camper_id == camper_id,
                                CampExtraCharge.camp_id == camp_id)).all())
                if camper_extra_charges:
                    for camper_extra_charge in camper_extra_charges:
                        camper_extra_charge_to_delete = db.query(CamperExtraCharge).filter(CamperExtraCharge.id == camper_extra_charge.id).first()
                        db.delete(camper_extra_charge_to_delete)
                
                camp_payments = db.query(Payment).where(and_(Payment.camp_id == camp_id, Payment.camper_id == camper_id)).all()
                if camp_payments:
                    for camp_payment in camp_payments:
                        db.delete(camp_payment) 

                db.delete(camper_in_camp)                
                db.flush()
            
            camp = db.query(Camp).filter(Camp.id == camp_id).first()
            extra_charges_camp = get_extra_charge_by_camp(db, camp.id)
            
            if extra_charges_camp:
                for extra_charge_camp in extra_charges_camp:
                    new_camper_extra_charge_obj = CamperExtraChargeCreate(
                        is_selected=False,
                        camper_id=camper.id,
                        extra_charge_id=extra_charge_camp.id
                        
                    )
                    create_new_camper_extra_charge_transaction(db, new_camper_extra_charge_obj)
                
            camp_extra_charges = (
                db.query(
                    Camp.id.label("camp_id"),
                    Camp.name.label("camp_name"),
                    CampExtraCharge.id.label("camp_extra_charge_id"),
                    CampExtraCharge.name.label("camp_extra_charge_name"),
                    CampExtraCharge.price.label("camp_extra_charge_price"),
                    CamperExtraCharge.id.label("camper_extra_charge_id"),
                    CamperExtraCharge.payment_id.label("camper_extra_charge_payment_id"),
                    CamperExtraCharge.is_selected.label("camp_extra_charge_is_selected"),
                )
                .outerjoin(
                    CamperExtraCharge,
                    CamperExtraCharge.extra_charge_id == CampExtraCharge.id,
                )
                .join(Camp, Camp.id == CampExtraCharge.camp_id)
                .filter(
                    and_(
                        CampExtraCharge.camp_id == camp_id,
                        CamperExtraCharge.camper_id == camper_id,
                    )
                )
                .all()
            )
            for camp_extra_charge in db_mapping_rows_to_dict(camp_extra_charges):
                extra_charges.append(camp_extra_charge)

            camp_extra_questions = get_extra_question_by_camp(db, camp.id)
            
            if camp_extra_questions:
                for camp_extra_question in camp_extra_questions:
                    new_camper_extra_answer_obj = CamperExtraAnswerCreate(
                        answer= '',
                        camper_id = camper.id,
                        question_id = camp_extra_question.id,
                                    
                    )
                    create_new_extra_answer_transaction(db, new_camper_extra_answer_obj)
            extra_questions = get_extra_answer_by_camper_camp(db, camper.id, camp.id)
            
            
            new_camper_in_camp = CamperInCampCreate(
                camper_id=camper_id,
                camp_id=camp_id,
                status=CAMP_STATUS_ENROLLED_ID,
                payment_balance=getattr(camp, "public_price"),
            )
            camper_in_camp_nw = create_new_camper_in_camp_transaction(db, new_camper_in_camp)
            
            # se genera el costo del camp
            payment = {
                "paid": False,
                "payment_amount": camp.public_price,
                "txn_number": "Camper:" + camper.name, 
                "camp_id": camp_id,
                "payment_date": datetime.now(),
                "camper_id": camper_id,
                "currency_id": camp.currency_id,
                "parent_id": parent["id"],
                "txn_type_id": TRANSACTION_TYPE_CAMP_PRICE_ID           
            }
            create_new_payment_transaction(db, payment)
    
        update_record_campers(db, camper_id)

        # enviamos un correo a los tutores de cuenta
        # tutor principal
        tutor_context = {
            "camper": camper_data_mailing,
            "user": parent,
            "camp": camp_data_mailing
        }
        # tutor secundario
        second_tutor_context = {
            "camper": camper_data_mailing,
            "user": second_parent,
            "camp": camp_data_mailing
        }

        send_mail_template(db, parent['email'],CAMP_REGISTRATION_PARENT_TEMPLATE_ID, tutor_context)
        send_mail_template(db, second_parent['email'],CAMP_REGISTRATION_PARENT_TEMPLATE_ID, second_tutor_context)
        
        # enviamos un correo a todas las cuentas admin    
        for admin_user in admin_users:
            admin_user_context = {
                "camper": camper_data_mailing,
                "user": admin_user,
                "camp": camp_data_mailing
            }  
            send_mail_template(db, admin_user['email'], CAMP_REGISTRATION_STAFF_TEMPLATE_ID, admin_user_context)
        
        # Aqui vamos a poner si ya tuvo un campamento previo o no.

        if prev_camper_in_camp:
            status_prev_sub = 1
        else:
            status_prev_sub = 0
        if extra_charges or extra_questions:
            return {
                "status": 2,
                "prev_camps": status_prev_sub,
                "extra_charges": extra_charges,
                "extra_questions": extra_questions,
            }
        else:
            return {"status": 1, "prev_camps": status_prev_sub}
    except Exception as ex:
        db.rollback()
        print(ex)
        return {"status": 3}

def update_camper_extra_charges(
    db,
    camper_id: int,
    extra_charges: "list[ExtraChargeMultiple]",
):
    if extra_charges:
        for extra_charge in extra_charges:
            camper_extra_charge = get_camper_extra_charge_by_id(db, extra_charge.camper_extra_charge_id)

            if extra_charge.camp_extra_charge_is_selected == True:
                if camper_extra_charge.payment_id == None:
                    try:
                        camp_extra_charge = get_extra_charge_by_id(db, camper_extra_charge.extra_charge_id)
                        parent = get_parent_by_camper_id(db, camper_id)
                        payment_extra_charge = {
                            "paid": False,
                            "payment_amount": int(extra_charge.camp_extra_charge_price),
                            "txn_number": "Costo extra" + " "+ extra_charge.camp_extra_charge_name,
                            "camp_id": extra_charge.camp_id,
                            "payment_date": datetime.now(),
                            "camper_id": camper_id,
                            "currency_id": camp_extra_charge.currency_id,
                            "parent_id": parent["id"],
                            "txn_type_id": TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID
                                
                        }
                        payment = create_new_payment_and_update_balance(db, payment_extra_charge)

                        camper_extra_charge.payment_id = payment.id
                        camper_extra_charge.is_selected = extra_charge.camp_extra_charge_is_selected;
                        db.commit()

                    except Exception as ex:
                        db.rollback()
                        print(ex)
                        return 3
                    
            if extra_charge.camp_extra_charge_is_selected == False:
                if camper_extra_charge.payment_id:
                    delete_payment_and_update_balance(db, camper_extra_charge.payment_id, camper_extra_charge.camper_id)
                    try:
                        camper_extra_charge.is_selected = extra_charge.camp_extra_charge_is_selected;
                        db.commit()
                    except Exception as ex:
                        db.rollback()
                        print(ex)
                        return 3
        return 1
                         


def create_update_camper_extras_camps(
    db,
    camper_id: int,
    extra_answers: list[ExtraAnswerMultiple],
    extra_charges: list[ExtraChargeMultiple],
):    
    
    if extra_answers:
        for extra_answer in extra_answers:
            if (
                db.query(CamperExtraAnswer)
                .filter(
                    and_(
                        CamperExtraAnswer.question_id
                        == extra_answer.camp_extra_question_id,
                        CamperExtraAnswer.camper_id == camper_id,
                    )
                )
                .update({"answer": getattr(extra_answer, "camp_extra_answer_answer")})
            ):
                db.commit()
            else:
                extra_answer_new = CamperExtraAnswerCreate(
                    answer=extra_answer.camp_extra_answer_answer,
                    camper_id=camper_id,
                    question_id=extra_answer.camp_extra_question_id,
                )
                status = create_new_extra_answer(db, extra_answer_new)

    if extra_charges:
        for extra_charge in extra_charges:
            if (
                db.query(CamperExtraCharge)
                .filter(
                    and_(
                        CamperExtraCharge.extra_charge_id
                        == extra_charge.camp_extra_charge_id,
                        CamperExtraCharge.camper_id == camper_id,
                    )
                )
                .update(
                    {
                        "is_selected": getattr(
                            extra_charge, "camp_extra_charge_is_selected"
                        )
                    }
                )
            ):
                print("updated")
                db.commit()
            else:
                print("executing")
                extra_charge_new = CamperExtraChargeCreate(
                    is_selected=extra_charge.camp_extra_charge_is_selected,
                    camper_id=camper_id,
                    extra_charge_id=extra_charge.camp_extra_charge_id,
                )
                created_extra_charge = create_new_camper_extra_charge(db, extra_charge_new)
                camp_extra_charge = get_extra_charge_by_id(db, created_extra_charge.extra_charge_id)
                parent = get_parent_by_camper_id(db, camper_id)
                payment_extra_charge = {
                    "paid": False,
                    "payment_amount": extra_charge.extra_charge_price,
                    "txn_number": "Costo extra" + extra_charge.extra_charge_name,
                    "camp_id": extra_charge.camp_id,
                    "payment_date": datetime.now(),
                    "camper_id": extra_charge.camper_id,
                    "currency_id": camp_extra_charge.currency_id,
                    "parent_id": parent["id"],
                    "txn_type_id": TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID    
                    
                }
                create_new_payment_and_update_balance(db, payment_extra_charge)
                
    return 1

def create_update_camper_extras_camp(
    db,
    camper_id: int,
    extra_answers: list[ExtraAnswerMultiple],
    extra_charges: list[ExtraChargeMultiple],
):    
    if extra_answers:
        for extra_answer in extra_answers:
            db_extra_answer = get_extra_answer_by_uuid(db, extra_answer.camper_extra_answer_id)
            try:
                db_extra_answer.answer = extra_answer.answer
                db.commit()
            except Exception as ex:
                db.rollback()
                print(ex)
                

    if extra_charges:
        for extra_charge in extra_charges:
            camper_extra_charge = get_camper_extra_charge_by_id(db, extra_charge.camper_extra_charge_id)

            if extra_charge.camp_extra_charge_is_selected == True:
                if camper_extra_charge.payment_id == None:
                    camp_extra_charge = get_extra_charge_by_id(db, camper_extra_charge.extra_charge_id)
                    parent = get_parent_by_camper_id(db, camper_id)
                    payment_extra_charge = {
                        "paid": False,
                        "payment_amount": int(extra_charge.camp_extra_charge_price),
                        "txn_number": "Costo extra" + " "+ extra_charge.camp_extra_charge_name,
                        "camp_id": extra_charge.camp_id,
                        "payment_date": datetime.now(),
                        "camper_id": camper_id,
                        "currency_id": camp_extra_charge.currency_id,
                        "parent_id": parent["id"],
                        "txn_type_id": TRANSACTION_TYPE_CAMP_ADDITIONAL_SERVICE_ID
                            
                    }
                    payment = create_new_payment_and_update_balance_transaction(db, payment_extra_charge)
                    try:
                        camper_extra_charge.payment_id = payment.id
                        camper_extra_charge.is_selected = extra_charge.camp_extra_charge_is_selected;
                        db.commit()
                    except Exception as ex:
                        db.rollback()
                        print(ex)
                    
            if extra_charge.camp_extra_charge_is_selected == False:
                if camper_extra_charge.payment_id:
                    delete_payment_and_update_balance(db, camper_extra_charge.payment_id, camper_extra_charge.camper_id)
                    try:
                        camper_extra_charge.is_selected = extra_charge.camp_extra_charge_is_selected;
                        db.commit()
                    except Exception as ex:
                        db.rollback()
                        print(ex)                
    return 1


def get_camper_in_camp_by_camper(db, camper_id: int):
    data = db.query(CamperInCamp).filter(CamperInCamp.camper_id == camper_id).all()
    return data

# def get_campers_in_camp_and_groupings(db, camp_id: int):
#     catalog_one = aliased(Constant)
#     catalog_two = aliased(Constant)
    
#     query = (
#         db.query(
#             Camper.id,
#             (Camper.name + ' ' + Camper.lastname_father + ' ' + Camper.lastname_mother).label('name'),
#             Camper.birthday,
#             catalog_one.value.label('gender'),
#             catalog_two.value.label('grade'),
#             func.string_agg(Grouping.name, ',').label('groupings')
#         )
#         .join(CamperInCamp, CamperInCamp.camper_id == Camper.id)
#         .join(catalog_one, Camper.gender_id == catalog_one.id)
#         .join(catalog_two, Camper.grade == catalog_two.id)
#         .outerjoin(GroupingCamper, Camper.id == GroupingCamper.camper_id)
#         .outerjoin(GroupingCamp, GroupingCamper.grouping_camp_id == GroupingCamp.id)
#         .outerjoin(Grouping, GroupingCamp.grouping_id == Grouping.id)
#         .filter(CamperInCamp.camp_id == camp_id)
#         .group_by(Camper.id, catalog_one.value, catalog_two.value)
#     )
    
#     data = db.execute(query)
#     return data.mappings().all()

def get_campers_in_camp_and_groupings(db, camp_id: int):
    catalog_one = aliased(Constant)
    catalog_two = aliased(Constant)
    
    campers_query = (
        db.query(
            Camper.id,
            (Camper.name + ' ' + Camper.lastname_father + ' ' + Camper.lastname_mother).label('name'),
            Camper.birthday,
            catalog_one.value.label('gender'),
            catalog_two.value.label('grade')
        )
        .join(CamperInCamp, CamperInCamp.camper_id == Camper.id)
        .join(catalog_one, Camper.gender_id == catalog_one.id)
        .join(catalog_two, Camper.grade == catalog_two.id)
        .where(CamperInCamp.camp_id == camp_id)

    )
    campers = db.execute(campers_query)
    campers = campers.mappings().all()
    
    campers_groupings_data = []
    for camper in campers:
        camper = dict(camper)
        campers_groupings_query = (
        db.query(
            Grouping.id,
            Grouping.name,
            GroupingType.id.label("grouping_type_id"),
            GroupingType.name.label("grouping_type_name"),
            GroupingCamper.id.label("grouping_camper_id")
        ).select_from(Grouping)
        .join(GroupingType, GroupingType.id == Grouping.grouping_type_id)
        .join(GroupingCamp, Grouping.id == GroupingCamp.grouping_id)
        .join(GroupingCamper, GroupingCamper.grouping_camp_id == GroupingCamp.id)
        .where(and_(GroupingCamper.camper_id == camper["id"], GroupingCamp.camp_id == camp_id))
        )
        campers_groupings = db.execute(campers_groupings_query)
        campers_groupings = campers_groupings.mappings().all()
        camper["groupings"] = campers_groupings
        campers_groupings_data.append(camper)
        
    return campers_groupings_data
"""
Camper extra charges
{
    is_selected = 
    extra_charge_id =
}

Camper extra questions
{
    answer =
    question_id = 
}


"""
