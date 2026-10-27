from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, and_
from model.mailings import (
    Campaign,
    CamperCampaign,
    StaffCampaign,
    SchoolCampaign,
    EmailTemplate,
)
from helper.mailing_helpers import send_mail_template, create_html_payment_table
from model.campers import Camper, School
from model.staffs import Staff
from model.user import User
from model.camps import Location
from model.camps.camper_in_camp import CamperInCamp
from model.catalogs import (Constant, Currency)
from model.campers.parent import Parent
from model.camps import Camp, Season
from model.trainings import Training, TrainingEvent
from model.payments.payment import Payment
from model.payments.payment_method import PaymentMethod
from model.payments.payment_transaction_type import PaymentTransactionType
from utils.db import db_mapping_rows_to_dict
from utils.payments.payment_table import create_payment_table, get_camper_balance_per_camp
from crud.campers.parent_crud import get_parent_by_camper_id, get_second_tutor_by_camper_id



def get_parent_by_id_mailing(db: Session, parent_id: int):
    query = db.query(Parent.tutor_name.label("name"),
             Parent.tutor_lastname_father.label("lastname_father"),
             Parent.tutor_lastname_mother.label("lastname_mother"),
             Parent.id,
             User.email         
             ).join(User, User.id == Parent.user_id).filter(Parent.id == parent_id)
    data = db.execute(query)
    return data.mappings().first()

def get_admin_users_for_mailing(db: Session):
    query = db.query(Staff.name,
                     Staff.id,
                     Staff.lastname_father,
                     Staff.lastname_mother,
                     User.email).join(User, User.id == Staff.login_id).filter(User.is_admin == True)
    data = db.execute(query)
    return data.mappings().all()

def get_camper_info_mailing(db: Session, camper_id: int):
    catalog_grade = aliased(Constant)
    query = db.query(
        Camper.id,
        Camper.name,
        func.concat(Camper.name, ' ', Camper.lastname_father, ' ', Camper.lastname_mother).label('fullname'),
        Camper.lastname_father,
        Camper.lastname_mother,
        catalog_grade.value.label('grade'),
        School.name.label("school")
    ).join(
        catalog_grade, Camper.grade == catalog_grade.id
    ).join(
        School,  School.id == Camper.school_id
    ).filter(Camper.id == camper_id)
    data = db.execute(query)
    return data.mappings().first()

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

def get_camp_info_by_id_mailing(db: Session, camp_id: int):
    query = db.query(Camp.id,
                     Camp.name,
                     Camp.start,
                     Camp.end,
                     Camp.start_registration,
                     Camp.end_registration,
                     Camp.registration,
                     Camp.url,
                     Camp.special_message,
                     Camp.special_message,
                     Camp.special_message_admin,
                     Camp.public_price,
                     Camp.insurance,
                     Camp.venue,
                     Camp.photo_url,
                     Camp.photo_password,
                     Camp.medical_report,
                     Camp.occupancy_camp,
                     School.name.label("school"),
                     Location.name.label("location")
                     ).join(School, School.id == Camp.school_id).join(Location, Location.id == Camp.location_id).filter(Camp.id == camp_id)
    data = db.execute(query)
    return data.mappings().first()

def get_staff_info_mailing(db: Session, staff_id: int):
    query = db.query(Staff.name,
                     Staff.lastname_father,
                     Staff.lastname_mother,
                     User.email).join(User, User.id == Staff.login_id).filter(Staff.id == staff_id)
    data = db.execute(query)
    return data.mappings().first()

def get_parent_info_mailing_by_camper_id(db, camper_id):
    
    query = db.query(Parent.tutor_name.label("name"),
                     Parent.id,
                     Parent.tutor_lastname_father.label("lastname_father"),
                     Parent.tutor_lastname_mother.label("lastname_mother"),
                     Parent.contact_email,
                     User.email).join(User, User.id == Parent.user_id).join(Camper, Camper.parent_id == Parent.id).filter(Camper.id == camper_id)
    data = db.execute(query)
    return data.mappings().first()

def get_second_parent_info_mailing_by_camper_id(db, camper_id):
    
    query = db.query(Parent.contact_name.label("name"),
                     Parent.id,
                     Parent.contact_name,
                     Parent.contact_lastname_father.label("lastname_father"),
                     Parent.contact_lastname_mother.label("lastname_mother"),
                     Parent.contact_email.label("email")
                     ).join(User, User.id == Parent.user_id).join(Camper, Camper.parent_id == Parent.id).filter(Camper.id == camper_id)
    data = db.execute(query)
    return data.mappings().first()


def get_camp_balance_mailing(db: Season, camper_id: int, camp_id: int):
    
    query = (db.query(CamperInCamp.payment_balance, Currency.acronyms, Currency.symbol)
             .select_from(CamperInCamp)
             .join(Camp, Camp.id == CamperInCamp.camp_id)
             .join(Currency, Currency.id == Camp.currency_id)
    .filter(and_(CamperInCamp.camp_id == camp_id, CamperInCamp.camper_id == camper_id)))
    data = db.execute(query)
    return data.mappings().first()

def get_camper_context_massive_mail(db: Session, camp_id: int, camper_id):
    
    user_info = get_parent_info_mailing_by_camper_id(db, camper_id)
    camp_info = get_camp_info_by_id_mailing(db, camp_id)
    camper_info = get_camper_info_mailing(db, camper_id)
    camp_total_balance = get_camp_balance_mailing(db, camper_id, camp_id)
    camper_payments_in_camp =  get_camper_payments_in_camp(db, camper_id, camp_id)
    payment_table = create_payment_table(db, camper_payments_in_camp)    
    payment_table_balance = create_html_payment_table(db, {"payments": payment_table})
    
    
    payment_default_variables = {
        "payment_date": "",
        "payment_method": "",
        "amount": "",
        "txn_type": "",
        "txn_number": ""
    }
    camper_balance = get_camper_balance_per_camp(db, camper_id, camp_id)
    formated_balance = camp_total_balance.symbol + "{:,.2f}".format(camper_balance) + camp_total_balance.acronyms
    
    context = {
        "camper": camper_info,
        "user": user_info,
        "camp": camp_info,
        "total_balance": formated_balance, 
        "payment": payment_default_variables,
        "show_table_balance": payment_table_balance
    }
    return context

def get_camper_context_second_parent_massive_mail(db: Session, camp_id: int, camper_id):
    
    user_info = get_second_parent_info_mailing_by_camper_id(db, camper_id)
    camp_info = get_camp_info_by_id_mailing(db, camp_id)
    camper_info = get_camper_info_mailing(db, camper_id)
    camp_total_balance = get_camp_balance_mailing(db, camper_id, camp_id)
    camper_payments_in_camp =  get_camper_payments_in_camp(db, camper_id, camp_id)
    payment_table = create_payment_table(db, camper_payments_in_camp)    
    payment_table_balance = create_html_payment_table(db, {"payments": payment_table})
    
    
    payment_default_variables = {
        "payment_date": "",
        "payment_method": "",
        "amount": "",
        "txn_type": "",
        "txn_number": ""
    }
    camper_balance = get_camper_balance_per_camp(db, camper_id, camp_id)
    formated_balance = camp_total_balance.symbol + "{:,.2f}".format(camper_balance) + camp_total_balance.acronyms
    
    context = {
        "camper": camper_info,
        "user": user_info,
        "camp": camp_info,
        "total_balance": formated_balance, 
        "payment": payment_default_variables,
        "show_table_balance": payment_table_balance
    }
    return context



def get_staff_context_system_mail(db: Session, staff_id):
    
    staff_info = get_staff_info_mailing(db, staff_id)
    
    default_camper_variables = {
        "name": "",
        "lastname_father" : "",
        "lastname_mother" : "",
        "fullname": "",
        "grade": "",
        "school": ""
    }
    default_camp_variables = {
        "id": "",
        "name": "",
        "start": "",
        "end": "",
        "start_registration": "",
        "end_registration": "",
        "registration": "",
        "url": "",
        "special_message": "",
        "special_message": "",
        "special_message_admin": "",
        "public_price": "",
        "insurance": "",
        "venue": "",
        "photo_url": "",
        "photo_password": "",
        "medical_report": "",
        "occupancy_camp": "",
        "school": "",
        "location": ""
        }          
    default_payment_variables = {
        "payment_date": "",
        "payment_method": "",
        "amount": "",
        "txn_type": "",
        "txn_number": ""
    }
    context = {
        "camper": default_camper_variables,
        "user": staff_info,
        "camp": default_camp_variables,
        "total_balance": "",
        "payment": default_payment_variables,
        "show_table_balance":""
    }
    return context

def get_staff_context_massive_mail(db: Session, staff_id, camp_id):
    
    staff_info = get_staff_info_mailing(db, staff_id)
    camp_info = get_camp_info_by_id_mailing(db, camp_id)
    default_camper_variables = {
        "name": "",
        "lastname_father" : "",
        "lastname_mother" : "",
        "fullname": "",
        "grade": "",
        "school": ""
    }

    default_payment_variables = {
        "payment_date": "",
        "payment_method": "",
        "amount": "",
        "txn_type": "",
        "txn_number": ""
    }
    context = {
        "camper": default_camper_variables,
        "user": staff_info,
        "camp": camp_info,
        "total_balance": "",
        "payment": default_payment_variables,
        "show_table_balance":""
    }
    return context




def get_public_for_campaign(db, campaign_id: int):
    campers = (
        db.query(
            Camper.id,
            (
                Camper.name
                + " "
                + Camper.lastname_father
                + " "
                + Camper.lastname_mother
            ).label("camper_fullname")
        )
        .select_from(CamperCampaign)
        .join(Camper, Camper.id == CamperCampaign.camper_id)
        .filter(CamperCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )

    staffs = (
        db.query(
            (
                Staff.name + " " + Staff.lastname_father + " " + Staff.lastname_mother
            ).label("staff_fullname")
        )
        .select_from(StaffCampaign)
        .join(Staff, Staff.id == StaffCampaign.staff_id)
        .filter(StaffCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )

    school = (
        db.query(School.name)
        .select_from(SchoolCampaign)
        .join(School, School.id == SchoolCampaign.school_id)
        .filter(SchoolCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )
    return {
        "campers": campers,
        "staffs": staffs,
        "school": school,
    }

def get_sent_camp(db, campaign_id: int):
    public_campaign = get_public_for_campaign(db, campaign_id)
    campaign = (
        db.query(
            Campaign.id.label("campaign_id"),
            Campaign.name.label("campaign_name"),
            Campaign.created_at.label("campaign_sent_date"),
            Camp.name.label("camp_name"),
            EmailTemplate.title.label("template_title"),
            EmailTemplate.template.label("template_body"),
        )
        .join(Camp, Camp.id == Campaign.camp_id)
        .join(EmailTemplate, EmailTemplate.id == Campaign.template_id)
        .filter(Campaign.id == campaign_id)
        .all()
    )
    return {
        "campers": public_campaign["campers"],
        "staffs": public_campaign["staffs"],
        "school": public_campaign["school"],
        "campaign_info": db_mapping_rows_to_dict(campaign)[0],
    }


def get_sent_camps(db, campaign_id: int):
    public_campaign = get_public_for_campaign(db, campaign_id)

    campaign = (
        db.query(
            Campaign.id.label("campaign_id"),
            Campaign.name.label("campaign_name"),
            Campaign.created_at.label("campaign_sent_date"),
            EmailTemplate.title.label("template_title"),
            EmailTemplate.template.label("template_body"),
        )
        .join(EmailTemplate, EmailTemplate.id == Campaign.template_id)
        .filter(Campaign.id == campaign_id)
        .all()
    )
    camps_unique = []
    camps_campers = (
        db.query(Camp.name)
        .select_from(CamperCampaign)
        .join(Camp, Camp.id == CamperCampaign.camp_id)
        .filter(CamperCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )
    [
        camps_unique.append(camp_camper)
        for camp_camper in camps_campers
        if camp_camper not in camps_unique
    ]
    camps_staffs = (
        db.query(Camp.name)
        .select_from(StaffCampaign)
        .join(Camp, Camp.id == StaffCampaign.camp_id)
        .filter(StaffCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )
    [
        camps_unique.append(camp_staff)
        for camp_staff in camps_staffs
        if camp_staff not in camps_unique
    ]
    camps_school = (
        db.query(Camp.name)
        .select_from(SchoolCampaign)
        .join(Camp, Camp.id == SchoolCampaign.camp_id)
        .filter(SchoolCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )
    [
        camps_unique.append(camp_school)
        for camp_school in camps_school
        if camp_school not in camps_unique
    ]

    return {
        "campers": public_campaign["campers"],
        "staffs": public_campaign["staffs"],
        "school": public_campaign["school"],
        "camps": db_mapping_rows_to_dict(camps_unique),
        "campaign_info": db_mapping_rows_to_dict(campaign)[0],
    }

def get_sent_training(db, campaign_id:int):

    campaign = (
        db.query(
            Campaign.id.label("campaign_id"),
            Campaign.name.label("campaign_name"),
            Campaign.created_at.label("campaign_sent_date"),
            Training.name.label("training_event"),
            TrainingEvent.start.label("training_start"),
            EmailTemplate.title.label("template_title"),
            EmailTemplate.template.label("template_body"),
        )
        .select_from(Campaign)
        .join(TrainingEvent, TrainingEvent.id == Campaign.training_event_id)
        .join(Training, Training.id == TrainingEvent.training_id)
        .join(EmailTemplate, EmailTemplate.id == Campaign.template_id)
        .filter(Campaign.id == campaign_id)
        .all()
    )

    staffs = (
        db.query(
            (
                Staff.name + " " + Staff.lastname_father + " " + Staff.lastname_mother
            ).label("staff_fullname")
        )
        .select_from(StaffCampaign)
        .join(Staff, Staff.id == StaffCampaign.staff_id)
        .filter(StaffCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )

    return {
        "staffs": staffs,
        "campaign_info": db_mapping_rows_to_dict(campaign)[0],
    }
    
    
def send_system_mail(db: Session, camper_id, camp_id, admin_template_id, parent_template_id):
    
    camper_data = get_camper_info_mailing(db, camper_id)
    camp_data = get_camp_info_by_id_mailing(db, camp_id)
    first_parent = get_parent_by_camper_id(db, camper_id)
    second_parent = get_second_tutor_by_camper_id(db, camper_id)
    admin_users = get_admin_users_for_mailing(db)
        
    tutor_context = {
        "camper": camper_data,
        "user": first_parent,
        "camp": camp_data
    }
    # tutor secundario
    second_tutor_context = {
        "camper": camper_data,
        "user": second_parent,
        "camp": camp_data
    }        
    send_mail_template(db, first_parent['email'], parent_template_id, tutor_context)
    send_mail_template(db, second_parent['email'], parent_template_id, second_tutor_context)
    
    for admin_user in admin_users:
        admin_user_context = {
            "camper": camper_data,
            "user": admin_user,
            "camp": camp_data
        }  
        send_mail_template(db, admin_user['email'],admin_template_id, admin_user_context)

    
    

def get_sent_candidates(db, campaign_id:int):

    campaign = (
        db.query(
            Campaign.id.label("campaign_id"),
            Campaign.name.label("campaign_name"),
            Campaign.created_at.label("campaign_sent_date"),
            Season.name.label("season_name"),
            EmailTemplate.title.label("template_title"),
            EmailTemplate.template.label("template_body"),
        )
        .select_from(Campaign)
        .join(Season, Season.id == Campaign.season_id)
        .join(EmailTemplate, EmailTemplate.id == Campaign.template_id)
        .filter(Campaign.id == campaign_id)
        .all()
    )

    staffs = (
        db.query(
            Staff.id, 
            (
                Staff.name + " " + Staff.lastname_father + " " + Staff.lastname_mother
            ).label("staff_fullname")
        )
        .select_from(StaffCampaign)
        .join(Staff, Staff.id == StaffCampaign.staff_id)
        .filter(StaffCampaign.campaign_id == campaign_id)
        .distinct()
        .all()
    )

    return {
        "staffs": staffs,
        "campaign_info": db_mapping_rows_to_dict(campaign)[0],
    }
    
def get_mailing_camps(db: Session):
    return db.query(Camp.id, Camp.name).order_by(Camp.name.asc()).all()
    
    # query = db.query(Camp.id, Camp.name).order_by(Camp.name.asc())
    # data = db.execute(query)
    # return data.mappings().all()