import os
from model.campers import Parent
from model.user import User
from model.campers import Camper
from model.staffs.staff import Staff
from helper.parent_helpers import append_campers_for_parent_admin
from schema.campers.parent_schema import ParentCreate, ParentModify
from schema.pagination.pagination_schema import Pagination, SortEnum
from sqlalchemy import or_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from utils.db import db_mapping_rows_to_dict
from helper.mailing_helpers import send_mail_template
from helper.pagination_helpers import get_number_of_pages, build_order_by
from crud.campers.camper_crud import get_campers_from_parent

import json

USER_EMAIL_WELCOME_TEMPLATE_ID = int(os.getenv("USER_EMAIL_WELCOME_TEMPLATE_ID"))
ADMIN_EMAIL_WELCOME_TEMPLATE_ID = int(os.getenv("ADMIN_EMAIL_WELCOME_TEMPLATE_ID"))


def get_all_parent(db: Session, pagination):
    order = desc if pagination.order == SortEnum.DESC else asc
    query = (
        db.query(Parent).select_from(Parent)
        .order_by(order(Parent.tutor_name))
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    
    rows_count = db.query(func.count(Parent.id)).select_from(Parent).scalar()
    pages = get_number_of_pages(rows_count, pagination.perPage)

    return {
        "pages": pages,
        "items": data,
        "total": rows_count
    }   


def get_parent_by_uuid(db: Session, parent_id: int):
    return db.query(Parent).filter_by(id=parent_id).first()


def get_parent_for_admin_by_id(db: Session, parent_id: int):
    parent = (
        db.query(
            User.id.label("user_id"),
            User.email.label("user_email"),
            Parent.id.label("tutor_id"),
            Parent.tutor_name.label("tutor_name"),
            Parent.tutor_lastname_father.label("tutor_lastname_father"),
            Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
            Parent.tutor_cellphone.label("tutor_cellphone"),
            Parent.tutor_home_phone.label("tutor_home_phone"),
            Parent.tutor_work_phone.label("tutor_work_phone"),
            Parent.contact_name.label("contact_name"),
            Parent.contact_lastname_father.label("contact_lastname_father"),
            Parent.contact_lastname_mother.label("contact_lastname_mother"),
            Parent.contact_cellphone.label("contact_cellphone"),
            Parent.contact_home_phone.label("contact_home_phone"),
            Parent.contact_work_phone.label("contact_work_phone"),
            Parent.contact_email.label("contact_email"),
        )
        .outerjoin(User, User.id == Parent.user_id)
        .filter(Parent.id == parent_id)
        .all()
    )
    if parent:
        return db_mapping_rows_to_dict(parent)[0]
    else:
        return "Parent doesn't exist"


def create_new_parent(db, new_parent: ParentCreate):
    db_parent = None
    try:
        db_parent = Parent(**new_parent.dict())
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
    except SQLAlchemyError as e:
        print("#=================================#")
        print(e)
        print("#=================================#")
        db_parent = None
        return db_parent
    except Exception as e:
        print(f"No se pudo guardar en la base de datos: {e}")
    return db_parent


def create_new_parent_user_id(db, new_parent: ParentCreate, user_id: int):
    db_parent = None
   
    try:
        new_parent.user_id = user_id
        user = db.query(User).filter(User.id == user_id).first()
        db_parent = Parent(**new_parent.dict())
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
        
            # send mail to parents
        parent = get_parent_by_id_mailing(db, db_parent.id)
        second_parent = get_second_tutor_by_parent_id(db, db_parent.id)
        
        parent_context = {
            "user": parent
        }
        second_parent_context = {
            "user": second_parent
        }
        
        send_mail_template(db, parent['email'], USER_EMAIL_WELCOME_TEMPLATE_ID, parent_context)
        send_mail_template(db, second_parent['email'], USER_EMAIL_WELCOME_TEMPLATE_ID, second_parent_context)

        admin_users = get_admin_users_for_mailing(db)

        for admin_user in admin_users:
            admin_user_context = {
                "user": admin_user
            }  
            send_mail_template(db, admin_user["email"], ADMIN_EMAIL_WELCOME_TEMPLATE_ID, admin_user_context)
        
    except Exception as e:
        print(e)
        if db_parent:
            db.delete(db_parent)
            db.commit()
        if user:
            db.delete(user)
            db.commit()            
        return None 
            
    return db_parent

def create_new_parent_user_id_transaction(db, new_parent: ParentCreate, user_id: int):
    db_parent = None
    new_parent.user_id = user_id
    user = db.query(User).filter(User.id == user_id).first()
    db_parent = Parent(**new_parent.dict())
    db.add(db_parent)
    db.flush()
    
        # send mail to parents
    parent = get_parent_by_id_mailing(db, db_parent.id)
    second_parent = get_second_tutor_by_parent_id(db, db_parent.id)
    
    parent_context = {
        "user": parent
    }
    second_parent_context = {
        "user": second_parent
    }
    
    send_mail_template(db, parent['email'], USER_EMAIL_WELCOME_TEMPLATE_ID, parent_context)
    send_mail_template(db, second_parent['email'], USER_EMAIL_WELCOME_TEMPLATE_ID, second_parent_context)

    admin_users = get_admin_users_for_mailing(db)

    for admin_user in admin_users:
        admin_user_context = {
            "user": admin_user
        }  
        send_mail_template(db, admin_user["email"], ADMIN_EMAIL_WELCOME_TEMPLATE_ID, parent_context )
    
    return db_parent


def get_second_tutor_by_parent_id(db: Session, parent_id: int):
    
    query = db.query(Parent.contact_name.label("name"),
                     Parent.id,
                     Parent.contact_lastname_father.label("lastname_father"),
                     Parent.contact_lastname_mother.label("lastname_mother"),
                     Parent.contact_email.label("email")).join(User, User.id == Parent.user_id).filter(Parent.id == parent_id)
    data = db.execute(query)
    return data.mappings().first()


def update_parent_by_id(db: Session, parent_id: int, modify_parent: ParentModify):
    rows_updated = (
        db.query(Parent)
        .filter_by(id=parent_id)
        .update(modify_parent, synchronize_session="fetch")
    )
    db.commit()
    return rows_updated


def get_parent_by_camper_id(db, camper_id):
    
    query = db.query(Parent.tutor_name.label("name"),
                     Parent.id,
                     Parent.tutor_lastname_father.label("lastname_father"),
                     Parent.tutor_lastname_mother.label("lastname_mother"),
                     Parent.contact_email,
                     User.email).join(User, User.id == Parent.user_id).join(Camper, Camper.parent_id == Parent.id).filter(Camper.id == camper_id)
    data = db.execute(query)
    return data.mappings().first()
 
def get_second_tutor_by_camper_id(db, camper_id):
    
    query = db.query(Parent.contact_name.label("name"),
                     Parent.id,
                     Parent.contact_lastname_father.label("lastname_father"),
                     Parent.contact_lastname_mother.label("lastname_mother"),
                     Parent.contact_email.label("email")).join(User, User.id == Parent.user_id).join(Camper, Camper.parent_id == Parent.id).filter(Camper.id == camper_id)
    data = db.execute(query)
    return data.mappings().first()


def delete_parent(db: Session, parent_id: int):
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    db.delete(parent)
    db.commit()
    return {"status": True}


def search_parent_by_name_user(db: Session, search: str):
    parents = (
        db.query(
            User.id.label("user_id"),
            Parent.id.label("tutor_id"),
            Parent.tutor_name.label("tutor_name"),
            Parent.tutor_lastname_father.label("tutor_lastname_father"),
            Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
            Parent.tutor_home_phone.label("tutor_home_phone"),
            Parent.tutor_work_phone.label("tutor_work_phone"),
            Parent.tutor_cellphone.label("tutor_cellphone"),
            User.email.label("tutor_email"),
            Parent.contact_email.label("second_tutor_email"),
        )
        .outerjoin(User, User.id == Parent.user_id)
        .filter(
            or_(
                Parent.tutor_name.ilike(r"%{}%".format(search)),
                Parent.contact_email.ilike(r"%{}%".format(search)),
                Parent.tutor_lastname_father.ilike(r"%{}%".format(search)),
                Parent.tutor_lastname_mother.ilike(r"%{}%".format(search)),
                User.email.ilike(r"%{}%".format(search)),
            )
        )
        .all()
    )

    if parents:
        possible_parents = append_campers_for_parent_admin(db, parents)
    else:
        possible_parents = []

    return possible_parents


PARENT_ADMIN_SORT_MAP = {
    "tutor_name": func.concat(Parent.tutor_name, ' ', Parent.tutor_lastname_father, ' ', Parent.tutor_lastname_mother),
    "tutor_cellphone": Parent.tutor_cellphone,
    "tutor_home_phone": Parent.tutor_home_phone,
    "tutor_email": User.email,
    "second_tutor_email": Parent.contact_email,
}

def get_all_parent_admin(db: Session, pagination):
    order = desc if pagination.order == SortEnum.DESC else asc
    data = []
    parents_query = (
        db.query(
            User.id.label("user_id"),
            Parent.id.label("tutor_id"),
            Parent.tutor_name.label("tutor_name"),
            Parent.tutor_lastname_father.label("tutor_lastname_father"),
            Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
            Parent.tutor_home_phone.label("tutor_home_phone"),
            Parent.tutor_work_phone.label("tutor_work_phone"),
            Parent.tutor_cellphone.label("tutor_cellphone"),
            User.email.label("tutor_email"),
            Parent.contact_email.label("second_tutor_email"),
        )
        .select_from(Parent)
        .join(User, User.id == Parent.user_id)
        .order_by(*build_order_by(pagination, PARENT_ADMIN_SORT_MAP, [order(Parent.created_at)], Parent.id))
        .limit(pagination.perPage)
        .offset((pagination.offset)) 
    )
    parents_data = db.execute(parents_query)
    parents_data = parents_data.mappings().all()
    rows_count = db.query(func.count(Parent.id)).select_from(Parent).join(User, User.id == Parent.user_id).scalar()
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    for parent in parents_data:
        campers = get_campers_from_parent(db, parent.tutor_id)
        parent_dict = dict(parent)
        parent_dict["campers"] = campers
        data.append(parent_dict)
    return  {
        "pages": pages,
        "items": data,
        "total": rows_count
        }
    
def search_all_parent_admin(db: Session, pagination, tutor_1_name: str, tutor_1_lastname_father: str, tutor_1_lastname_mother: str, tutor_1_email: str, tutor_2_name: str, tutor_2_lastname_father: str,tutor_2_lastname_mother: str, tutor_2_email: str):
    data = []
    parents_query = (
        db.query(
            User.id.label("user_id"),
            Parent.id.label("tutor_id"),
            Parent.tutor_name.label("tutor_name"),
            Parent.tutor_lastname_father.label("tutor_lastname_father"),
            Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
            Parent.tutor_home_phone.label("tutor_home_phone"),
            Parent.tutor_work_phone.label("tutor_work_phone"),
            Parent.tutor_cellphone.label("tutor_cellphone"),
            User.email.label("tutor_email"),
            Parent.contact_email.label("second_tutor_email"),
        ).select_from(Parent)
        .join(User, User.id == Parent.user_id)
        .filter(
            or_(
                User.email.op('%')(tutor_1_email),
                Parent.tutor_name.op('%')(tutor_1_name),
                Parent.tutor_lastname_father.op('%')(tutor_1_lastname_father),
                Parent.tutor_lastname_mother.op('%')(tutor_1_lastname_mother),
                Parent.contact_name.op('%')(tutor_2_name),
                Parent.contact_lastname_father.op('%')(tutor_2_lastname_father),
                Parent.contact_lastname_mother.op('%')(tutor_2_lastname_mother),
                Parent.contact_email.op('%')(tutor_2_email),
            ) 
        )
        .order_by(*build_order_by(pagination, PARENT_ADMIN_SORT_MAP, [
            func.similarity(User.email, tutor_1_email).desc(),
            func.similarity(Parent.tutor_name, tutor_1_name).desc(),
            func.similarity(Parent.tutor_lastname_father, tutor_1_lastname_father).desc(),
            func.similarity(Parent.tutor_lastname_mother, tutor_1_lastname_mother).desc(),
            func.similarity(Parent.contact_name, tutor_2_name).desc(),
            func.similarity(Parent.contact_lastname_father, tutor_2_lastname_father).desc(),
            func.similarity(Parent.contact_lastname_mother, tutor_2_lastname_mother).desc(),
            func.similarity(Parent.contact_email, tutor_2_email).desc()
        ], Parent.id))
        .limit(pagination.perPage)
        .offset((pagination.offset)) 
    )
    parents_data = db.execute(parents_query)
    parents_data = parents_data.mappings().all()
    rows_count = (
        db.query(func.count(Parent.id)).select_from(Parent).join(User, User.id == Parent.user_id).filter(
            or_(
                User.email.op('%')(tutor_1_email),
                Parent.tutor_name.op('%')(tutor_1_name),
                Parent.tutor_lastname_father.op('%')(tutor_1_lastname_father),
                Parent.tutor_lastname_mother.op('%')(tutor_1_lastname_mother),
                Parent.contact_name.op('%')(tutor_2_name),
                Parent.contact_lastname_father.op('%')(tutor_2_lastname_father),
                Parent.contact_lastname_mother.op('%')(tutor_2_lastname_mother),
                Parent.contact_email.op('%')(tutor_2_email),
            ) 
        ).scalar()
                  
    )
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    for parent in parents_data:
        campers = get_campers_from_parent(db, parent.tutor_id)
        parent_dict = dict(parent)
        parent_dict["campers"] = campers
        data.append(parent_dict)
    return  {
        "pages": pages,
        "items": data,
        "total": rows_count
        }
    
 
 
 
   

    # return possible_parents
# Se agrega esta función de forma temporal debido a un error de importación
def get_admin_users_for_mailing(db: Session):
    query = db.query(Staff.name,
                     Staff.id,
                     Staff.lastname_father,
                     Staff.lastname_mother,
                     User.email).join(User, User.id == Staff.login_id).filter(User.is_admin == True)
    data = db.execute(query)
    return data.mappings().all()


# Se agrega esta función de forma temporal debido a un error de importación
def get_parent_by_id_mailing(db: Session, parent_id: int):
    query = db.query(Parent.tutor_name.label("name"),
             Parent.tutor_lastname_father.label("lastname_father"),
             Parent.tutor_lastname_mother.label("lastname_mother"),
             Parent.id,
             User.email         
             ).join(User, User.id == Parent.user_id).filter(Parent.id == parent_id)
    data = db.execute(query)
    return data.mappings().first()