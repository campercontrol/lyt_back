import os
from sqlalchemy import case, or_, and_, asc, desc
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete
from sqlalchemy.orm import class_mapper
from sqlalchemy import func
from model.role import Role
from model.user import User
from model.campers import School
from model.campers import Camper
from model.campers import Parent
from model.staffs import Staff
from model.camps.camper_in_camp import CamperInCamp
from model.medical import Doctor
from model.camps import Camp
from utils.hash import hash_str
from utils.db import db_mapping_rows_to_dict
from datetime import date, timedelta
from crud.payments.payment_crud import get_all_camper_payments
from crud.camps.staff_in_camp_crud import get_staff_all_camps_by_staff_id
from crud.trophies.trophy_staff_crud import get_all_staff_trophies
from crud.training.staff_in_training_crud import get_all_staff_training
from crud.campers.camper_crud import get_campers_in_school
from crud.campers.parent_crud import create_new_parent_user_id, create_new_parent_user_id_transaction
from schema.pagination.pagination_schema import Pagination, SortEnum
from helper.pagination_helpers import get_number_of_pages


ROLE_PARENT_ID = int(os.getenv("ROLE_PARENT_ID"))
ROLE_STAFF_ID = int(os.getenv("ROLE_STAFF_ID"))
ROLE_SCHOOL_ID = int(os.getenv("ROLE_SCHOOL_ID"))
ROLE_TEACHER_ID =  int(os.getenv("ROLE_TEACHER_ID"))
ROLE_DOCTOR_ID = int(os.getenv("ROLE_DOCTOR_ID"))  


def get_all_user(db, is_active, pagination):
    order = desc if pagination.order == SortEnum.DESC else asc
    
    query = (
        db.query(
            User.id.label('id'),
            User.email.label('email'),
            User.hashed_pass.label('hashed_pass'),
            User.role_id.label('role_id'),
            Role.name.label('role_name'),
            User.is_admin,
            User.is_coordinator,
            User.is_employee,
            User.is_superuser.label('is_superuser'),
            User.is_active.label('is_active'),
        )
        .join(
            Role, Role.id == User.role_id
        ).filter(
            User.is_active == is_active,
        )
        .order_by(order(User.created_at))
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = db.query(func.count(User.id)).select_from(User).join(Role, Role.id == User.role_id).filter(User.is_active == is_active).scalar()
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    return  {
        "pages": pages,
        "items": data,
        "total": rows_count
        }

def search_all_user(db, is_active, pagination, email):
    
    query = (
        db.query(
            User.id.label('id'),
            User.email.label('email'),
            User.hashed_pass.label('hashed_pass'),
            User.role_id.label('role_id'),
            Role.name.label('role_name'),
            User.is_admin,
            User.is_coordinator,
            User.is_employee,
            User.is_superuser.label('is_superuser'),
            User.is_active.label('is_active'),
        )
        .join(
            Role, Role.id == User.role_id
        ).filter(
            User.is_active == is_active,
        )
        .filter(
            User.email.op('%')(email)
        )
        .order_by(
            func.similarity(User.email, email).desc()
        )
        .limit(pagination.perPage)
        .offset((pagination.offset))
    )
    data = db.execute(query)
    data = data.mappings().all()
    rows_count = (db.query(func.count(User.id))
        .select_from(User)
        .join(Role, Role.id == User.role_id)
        .filter(User.is_active == is_active)
        .filter(
            User.email.op('%')(email)
        ).scalar())
    pages = get_number_of_pages(rows_count, pagination.perPage)
    
    return  {
        "pages": pages,
        "items": data,
        "total": rows_count
        }
    

def get_users_all_info(db, user_id):
    query = db.query(
        User.id,
        User.email,
        Parent.tutor_name,
        Parent.tutor_lastname_father,
        Parent.tutor_lastname_mother
    ).join(Parent, User.id == Parent.user_id).filter(User.id == user_id)
    data = db.execute(query)
    parent = data.mappings().first()
    print(parent)
    
def get_subscribe_by_camper(db: Session, camper_id: int):
    query = db.query(
                Camp.id.label("camp_id"),
                Camp.name,
            ).join(CamperInCamp, CamperInCamp.camp_id == Camp.id).filter(CamperInCamp.camper_id == camper_id)
    data = db.execute(query)
    data = data.mappings().all()
    return data
    
def get_all_school_camps(db: Session, school_id: str):
    query = db.query(Camp.name).filter(Camp.school_id == school_id)
    data = db.execute(query)
    data = data.mappings().all()
    return data
    
def get_user_delete_info(db, user_id):
    user = db.query(User).filter(User.id==user_id).first()
    
    if not user:
        return None 
    
    
    if user.role_id == ROLE_PARENT_ID:
        parent = db.query(Parent).filter_by(user_id=user.id).first()
        
        campers = db.query(Camper).filter_by(parent_id = parent.id).all()
        campers_info = []
        for camper in campers:
            camps = get_subscribe_by_camper(db, camper.id)
            payments = get_all_camper_payments(db, camper.id)
            camper_obj = {
                "camper_fullname": camper.name + ' ' + camper.lastname_father + ' ' + camper.lastname_mother,
                "camps": camps,
                "payments": payments
            }
            campers_info.append(camper_obj)
        parent_info = {
            "id": parent.id,
            "role_id": user.role_id,
            "parent_fullname": parent.tutor_name + ' ' + parent.tutor_lastname_father + ' ' + parent.tutor_lastname_mother,
            "campers": campers_info
        }
        return parent_info             
    if user.role_id == ROLE_STAFF_ID:
        staff = db.query(Staff).filter_by(login_id=user.id).first()
        staff_camps = get_staff_all_camps_by_staff_id(db, staff.id)
        trophies = get_all_staff_trophies(db, staff.id)
        trainings = get_all_staff_training(db, staff.id)

        staff_info = {
            "id": staff.id,
            "role_id": user.role_id,
            "staff_fullname": staff.name + ' ' + staff.lastname_father + ' ' + staff.lastname_mother,
            "staff_in_camp": staff_camps,
            "trophies": trophies,
            "trainings": trainings
        }
        return staff_info
    
    if user.role_id == ROLE_DOCTOR_ID:
        doctor = db.query(Doctor).filter_by(login_id=user.id).first()

        doctor_info = {
            "id": doctor.id,
            "role_id": user.role_id,
            "doctor_fullname": doctor.name + ' ' + doctor.lastname_father + ' ' + doctor.lastname_mother,
        }
        return doctor_info
        
    if user.role_id == ROLE_SCHOOL_ID:
        school = db.query(School).filter_by(login_id=user.id).first()
        school_camps = get_all_school_camps(db, school.id)
        school_campers = get_campers_in_school(db, school.id)
        school_info = {
            "id": school.id,
            "role_id": user.role_id,
            "school_name": school.name,
            "school_camps": school_camps,
            "school_campers": school_campers
        }
        return school_info
        
    
def create_new_user(db, new_user):
    db_user = None
    try:
        db_user = User(
            email=new_user.email,
            hashed_pass=hash_str(new_user.passw),
            role_id=new_user.role_id,
            is_superuser=new_user.is_superuser                
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        db.rollback()
        print("#=================")
        print(e)
        print("#=================")
        db_user = None
        return db_user
    except Exception as ex:
        db.rollback()
        db_user = None
        print(f"No se pudo guardar en la base de datos: {ex}")
    return db_user



def create_new_user_transaction(db, new_user):
    db_user = User(
        email=new_user.email,
        hashed_pass=hash_str(new_user.passw),
        role_id=new_user.role_id,
        is_superuser=new_user.is_superuser                
    )
    db.add(db_user)
    db.flush()
    return db_user

def create_parent_complete(db: Session, new_parent_complete):
   
    try: 
        user = get_user_by_email(db, new_parent_complete.user.email)

        if user:
            return 2
        user = create_new_user_transaction(db, new_parent_complete.user)
        create_new_parent_user_id_transaction(db, new_parent_complete.parent, user.id)
        db.commit()
        return 1
    except Exception as ex:
        db.rollback()
        print(ex)
        return 3

def create_new_user_admin(db, new_user):
    db_user = User(
        email=new_user.email,
        hashed_pass=hash_str(new_user.passw),
        role_id=new_user.role_id,
        is_superuser=new_user.is_superuser,
        is_coordinator = new_user.is_coordinator,
        is_admin = new_user.is_admin,
        is_employee = new_user.is_employee,
        is_active = new_user.is_active
                        
    )
    db.add(db_user)
    db.flush()
    return db_user


def create_new_prospect_user(db, new_user):
    db_user = None
    try:
        db_user = User(
            email=new_user.email,
            hashed_pass=hash_str(new_user.passw),
            role_id= ROLE_STAFF_ID,
            is_active= False,
            is_coordinator = False,
            is_admin = False,
            is_employee = False,
            is_superuser = False           
                 
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        print("#=================")
        print(e)
        print("#=================")
        db_user = None
        return db_user
    except Exception as ex:
        db_user = None
        print(f"No se pudo guardar en la base de datos: {ex}")
    return db_user



def get_user_by_uuid(db, user_id):
    rows = []
    first_row = (
        db.query(
            User.id.label('id'),
            User.email.label('email'),
            User.hashed_pass.label('hashed_pass'),
            User.role_id.label('role_id'),
            Role.name.label('role_name'),
            User.is_admin,
            User.is_coordinator,
            User.is_employee,
            User.is_superuser.label('is_superuser'),
            User.is_active.label('is_active'),
        )
        .join(
            Role, Role.id == User.role_id
        ).filter(
            User.id == user_id
        )
        .first()
    )
    rows.append(first_row)

    return db_mapping_rows_to_dict(rows)


def crud_update_user_by_uuid(db, user_id, update_data):

    print(f"user_id:{user_id}")
    print(f"update_data:{update_data}")

    rows_updated = db.query(
    User
    ).filter_by(
        id = user_id,
    ).update(
        update_data,
        synchronize_session="fetch",
    )
    db.commit()
    print(f"rows_updated:{rows_updated}")
    return rows_updated

def crud_update_user_by_email(db, email, update_data):

    print(f"email:{email}")
    print(f"update_data:{update_data}")

    rows_updated = db.query(
    User
    ).filter_by(
        email = email,
    ).update(
        update_data,
        synchronize_session="fetch",
    )
    db.commit()
    print(f"rows_updated:{rows_updated}")
    return rows_updated

# ==========Login
def get_user_by_email(db, email):
    return db.query(User).filter_by(email=email).first()


def get_user_info_by_email(db: Session, email: str):
    user = db.query(User).filter_by(email=email).first()
    
    if user.role_id == ROLE_PARENT_ID:
        user_info_query = db.query(User.email, Parent.tutor_name.label("name")).join(Parent, Parent.user_id == User.id).filter(User.email == email)
        user_info = db.execute(user_info_query)
        user_info = user_info.mappings().first()
    if user.role_id == ROLE_SCHOOL_ID:
        user_info_query = db.query(User.email, School.name).join(School, School.login_id == User.id).filter(User.email == email)
        user_info = db.execute(user_info_query)
        user_info = user_info.mappings().first()
    if user.role_id == ROLE_STAFF_ID:
        user_info_query = db.query(User.email, Staff.name.label("name")).join(Staff, Staff.login_id == User.id).filter(User.email == email)
        user_info = db.execute(user_info_query)
        user_info = user_info.mappings().first()
    if user.role_id == ROLE_DOCTOR_ID:
        user_info_query = db.query(User.email, Doctor.name.label("name")).join(Doctor, Doctor.login_id == User.id).filter(User.email == email)
        user_info = db.execute(user_info_query)
        user_info = user_info.mappings().first()
    
    return user_info
    
        
    
    

def get_profile_id_by_user_id(db, user_id:int ):
    

    profile_id = ['']
    user_role = (
        db.query(User.role_id)
        .filter_by(id = user_id)
        .first()
    )
    # print("get profile ===============")
    # print(user_role[0])
    
    if user_role[0] == ROLE_PARENT_ID:
        profile_id = (
            db.query(Parent.id)
            .join(User, User.id == Parent.user_id)
            .filter( Parent.user_id == user_id)
            .first()
        )

    if user_role[0] == ROLE_STAFF_ID:
        profile_id = (
            db.query(Staff.id)
            .join(User, User.id == Staff.login_id)
            .filter( Staff.login_id == user_id)
            .first()
        )
    if user_role[0] == ROLE_SCHOOL_ID:
        profile_id = (
            db.query(School.id)
            .join(User, User.id == School.login_id)
            .filter(School.login_id == user_id)
            .first()
        )
    if user_role[0] == ROLE_DOCTOR_ID:
        profile_id = (
            db.query(Doctor.id)
            .join(User, User.id == Doctor.login_id)
            .filter(Doctor.login_id == user_id)
            .first()
        )
    return profile_id[0]

def search_user_by_email(db: Session, search: str):
    users = (
        db.query(
            User.id.label("user_id"),
            User.email.label("tutor_email"),
            User.is_active.label("user_active"),
            User.is_superuser.label("user_superuser"),
            User.is_employee.label("user_employee"),
            User.is_coordinator.label("user_coordinator"),
            User.is_admin.label("user_admin"),
            User.created_at.label("user_created")
        )        
        .filter(
            User.email.ilike(r"%{}%".format(search))
        )
        .all()
    )
    if users:
        return db_mapping_rows_to_dict(users)
    else:
        return "Data not found"

def update_user_by_id(db: Session, user_id:int, user_data):
    
    print(user_data)
    # if user_data['hashed_pass']:
    # user_data['hashed_pass'] = hash_str(user_data['hashed_pass'])
    

    try:
        user_to_update = db.query(User).filter_by(id=user_id).one()
        
        if user_data['hashed_pass'] != None:
            user_to_update.hashed_pass = hash_str(user_data['hashed_pass'])
        if user_data['role_id'] != None:
            user_to_update.role_id = user_data['role_id']
        if user_data['is_admin'] != None:
            user_to_update.is_admin = user_data['is_admin']
        if user_data['is_superuser'] != None:
            user_to_update.is_superuser = user_data['is_superuser']
        if user_data['is_coordinator'] != None:
            user_to_update.is_coordinator = user_data['is_coordinator']
        if user_data['is_employee'] != None:
            user_to_update.is_employee = user_data['is_employee'] 
        if user_data['is_active'] != None:
            user_to_update.is_active = user_data['is_active']       
        if user_data['email'] != None:
            user_to_update.email = user_data['email']
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(e)
        return {"status": 3, "msg": "Internal server error"}
    return {"status": 1, "msg": "User updated successfully"}


def delete_user_by_id(db: Session, user_id:int):

    user = db.query(User).filter(User.id==user_id).first()
    
    
    if user.role_id == ROLE_PARENT_ID:
        try:
            parent_user = db.query(Parent).filter(Parent.user_id == user.id).first()
            stmt_delete_user = delete(User).where(User.id == user.id)
            db.execute(stmt_delete_user)
            db.commit()
        except IntegrityError as IntegrityEx:
            db.rollback()
            print(IntegrityEx)
            return {"status": 2, "msg": "Can not delete Parent user, referenced by other table"}
        except Exception as ex:
            db.rollback()
            print(ex)
            return {"status": 3, "msg": "An unknown error ocurred while deleting"}
        return {"status": 1, "msg": "Parent user succesfully deleted"}
        
    if user.role_id == ROLE_STAFF_ID:
        try:
            stmt_delete_user = delete(User).where(User.id == user.id)
            db.execute(stmt_delete_user)
            db.commit()
        except IntegrityError as IntegrityEx:
            db.rollback()
            print(IntegrityEx)
            return {"status": 2, "msg": "Can not staff user, Staff user referenced by other table"}
        except Exception as ex:
            db.rollback()
            print(ex)
            return {"status": 3, "msg": "An unknown error ocurred while deleting"}
        return {"status": 1, "msg": "Staff user succesfully deleted"}
        
    if user.role_id == ROLE_SCHOOL_ID:
        try: 
            stmt_delete_user = delete(User).where(User.id == user.id)
            db.execute(stmt_delete_user)
            db.commit()
        except IntegrityError as IntegrityEx:
            db.rollback()
            print(IntegrityEx)
            return {"status": 2, "msg": "Can not delete School user, School referenced by camps camp"}
        except Exception as ex:
            return {"status": 3, "msg": "An unknown error ocurred while deleting"}
        return {"status": 1, "msg": "School user succesfully deleted"}
    
    if user.role_id == ROLE_DOCTOR_ID:
        try:
            stmt_delete_user = delete(User).where(User.id == user.id)
            db.execute(stmt_delete_user)
            db.commit()
        except IntegrityError as IntegrityEx:
            db.rollback()
            print(IntegrityEx)
            return {"status": 2, "msg": "Can not delete Medical user, referenced by other table"}
        except Exception as ex:
            return {"status": 3, "msg": "An unknown error ocurred while deleting"}
        return {"status": 1, "msg": "Medical user succesfully deleted"}
    
