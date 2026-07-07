import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from model.campers import CamperComment
from model.role import Role
from model.user import User
from model.staffs.staff import Staff
from model.campers.camper import Camper
from model.campers.parent import Parent
from model.campers.school import School
from model.medical.doctor import Doctor
from schema.campers.camper_comment_schema import (
    CamperCommentCreate,
    CamperCommentModify,
)
from utils.db import db_mapping_rows_to_dict
from sqlalchemy import case, and_, or_


ROLE_PARENT_ID = int(os.getenv("ROLE_PARENT_ID"))
ROLE_STAFF_ID = int(os.getenv("ROLE_STAFF_ID"))
ROLE_SCHOOL_ID = int(os.getenv("ROLE_SCHOOL_ID")) 
ROLE_TEACHER_ID = int(os.getenv("ROLE_TEACHER_ID"))
ROLE_DOCTOR_ID = int(os.getenv("ROLE_DOCTOR_ID"))


def get_all_camper_comment(db):
    rows = db.query(CamperComment).all()
    return rows


def get_camper_comment_by_id(db, camper_comment_id: int):
    return db.query(CamperComment).filter_by(id=camper_comment_id).first()


def get_all_camper_comments_by_camper_id(db, camper_id: int):
    query = (db.query(
                CamperComment.id,
                CamperComment.comment,
                CamperComment.is_public,
                CamperComment.show_to,
                CamperComment.camp_id,
                CamperComment.camper_id,
                CamperComment.user_id,
                User.role_id
                      
                      )
            .join(User, User.id == CamperComment.user_id)
            .filter(CamperComment.camper_id == camper_id)
    )
    rows = db.execute(query)
    rows = rows.mappings().all()
    return rows

def get_camper_comments_by_camper_id(db, camper_id: int, role_id: int):
    data = []
    comments = []
    if role_id == 1:
        query = (
            db.query(
                CamperComment.id,
                CamperComment.comment,
                User.id.label("user_id"),
                Role.name.label("role_name"),
                Parent.id.label("parent_id"),
                Parent.tutor_name.label("tutor_name"),
                Parent.tutor_lastname_father.label("tutor_lastname_father"),
                Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
                School.id.label("school_id"),
                School.name.label('school_name'),
                Staff.id.label("staff_id"),
                Staff.name.label('staff_name'), 
                Staff.lastname_father.label('staff_lastname_father'), 
                Staff.lastname_mother.label('staff_lastname_mother'),
                Doctor.id.label("doctor_id"),
                Doctor.name.label('doctor_name'),
                Doctor.lastname_father.label('doctor_lastname_father'),
                Doctor.lastname_mother.label('doctor_lastname_mother')
            )
            .select_from(CamperComment)
            .join(User, User.id == CamperComment.user_id)
            .join(Role, Role.id == User.role_id)
            .join(Parent, Parent.user_id == User.id, isouter = True)
            .join(School, School.login_id == User.id, isouter = True)
            .join(Staff, Staff.login_id == User.id, isouter = True)
            .join(Doctor, Doctor.login_id == User.id, isouter = True)          
            .filter(
                and_(
                    CamperComment.camper_id == camper_id,
                    CamperComment.show_to == 1
                )
            )
            
        )
        comments = db.execute(query)
        comments = comments.mappings().all()
        
    elif role_id == 3:
        query = (
            db.query(
                CamperComment.id,
                CamperComment.comment,
                User.id.label("user_id"),
                Role.name.label("role_name"),
                Parent.id.label("parent_id"),
                Parent.tutor_name.label("tutor_name"),
                Parent.tutor_lastname_father.label("tutor_lastname_father"),
                Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
                School.id.label("school_id"),
                School.name.label('school_name'),
                Staff.id.label("staff_id"),
                Staff.name.label('staff_name'), 
                Staff.lastname_father.label('staff_lastname_father'), 
                Staff.lastname_mother.label('staff_lastname_mother'),
                Doctor.id.label("doctor_id"),
                Doctor.name.label('doctor_name'),
                Doctor.lastname_father.label('doctor_lastname_father'),
                Doctor.lastname_mother.label('doctor_lastname_mother')
            )
            .select_from(CamperComment)
            .join(User, User.id == CamperComment.user_id)
            .join(Role, Role.id == User.role_id)
            .join(Parent, Parent.user_id == User.id, isouter = True)
            .join(School, School.login_id == User.id, isouter = True)
            .join(Staff, Staff.login_id == User.id, isouter = True)
            .join(Doctor, Doctor.login_id == User.id, isouter = True)          
            .filter(
                CamperComment.camper_id == camper_id,
                or_(
                    CamperComment.show_to==1,
                    CamperComment.show_to==3,
                )
            )
        ) 
        comments = db.execute(query)
        comments = comments.mappings().all()
    elif role_id == 5:
        query = (
            db.query(
                CamperComment.id,
                CamperComment.comment,
                User.id.label("user_id"),
                Role.name.label("role_name"),
                Parent.id.label("parent_id"),
                Parent.tutor_name.label("tutor_name"),
                Parent.tutor_lastname_father.label("tutor_lastname_father"),
                Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
                School.id.label("school_id"),
                School.name.label('school_name'),
                Staff.id.label("staff_id"),
                Staff.name.label('staff_name'), 
                Staff.lastname_father.label('staff_lastname_father'), 
                Staff.lastname_mother.label('staff_lastname_mother'),
                Doctor.id.label("doctor_id"),
                Doctor.name.label('doctor_name'),
                Doctor.lastname_father.label('doctor_lastname_father'),
                Doctor.lastname_mother.label('doctor_lastname_mother')
            )
            .select_from(CamperComment)
            .join(User, User.id == CamperComment.user_id)
            .join(Role, Role.id == User.role_id)
            .join(Parent, Parent.user_id == User.id, isouter = True)
            .join(School, School.login_id == User.id, isouter = True)
            .join(Staff, Staff.login_id == User.id, isouter = True)
            .join(Doctor, Doctor.login_id == User.id, isouter = True)          
            .filter(
                CamperComment.camper_id == camper_id,
                or_(
                    CamperComment.show_to==1,
                    CamperComment.show_to==5,
                )
            )
        ) 
        comments = db.execute(query)
        comments = comments.mappings().all()
    elif role_id == 6:
        query = (
            db.query(
                CamperComment.id,
                CamperComment.comment,
                User.id.label("user_id"),
                Role.name.label("role_name"),
                Parent.id.label("parent_id"),
                Parent.tutor_name.label("tutor_name"),
                Parent.tutor_lastname_father.label("tutor_lastname_father"),
                Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
                School.id.label("school_id"),
                School.name.label('school_name'),
                Staff.id.label("staff_id"),
                Staff.name.label('staff_name'), 
                Staff.lastname_father.label('staff_lastname_father'), 
                Staff.lastname_mother.label('staff_lastname_mother'),
                Doctor.id.label("doctor_id"),
                Doctor.name.label('doctor_name'),
                Doctor.lastname_father.label('doctor_lastname_father'),
                Doctor.lastname_mother.label('doctor_lastname_mother')
            )
            .select_from(CamperComment)
            .join(User, User.id == CamperComment.user_id)
            .join(Role, Role.id == User.role_id)
            .join(Parent, Parent.user_id == User.id, isouter = True)
            .join(School, School.login_id == User.id, isouter = True)
            .join(Staff, Staff.login_id == User.id, isouter = True)
            .join(Doctor, Doctor.login_id == User.id, isouter = True)          
            .filter(
                CamperComment.camper_id == camper_id,
                or_(
                    CamperComment.show_to==1,
                    CamperComment.show_to==6,
                )
            )
        ) 
        comments = db.execute(query)
        comments = comments.mappings().all()
    elif role_id == 7:
        query = (
            db.query(
                CamperComment.id,
                CamperComment.comment,
                User.id.label("user_id"),
                Role.name.label("role_name"),
                Parent.id.label("parent_id"),
                Parent.tutor_name.label("tutor_name"),
                Parent.tutor_lastname_father.label("tutor_lastname_father"),
                Parent.tutor_lastname_mother.label("tutor_lastname_mother"),
                School.id.label("school_id"),
                School.name.label('school_name'),
                Staff.id.label("staff_id"),
                Staff.name.label('staff_name'), 
                Staff.lastname_father.label('staff_lastname_father'), 
                Staff.lastname_mother.label('staff_lastname_mother'),
                Doctor.id.label("doctor_id"),
                Doctor.name.label('doctor_name'),
                Doctor.lastname_father.label('doctor_lastname_father'),
                Doctor.lastname_mother.label('doctor_lastname_mother')
            )
            .select_from(CamperComment)
            .join(User, User.id == CamperComment.user_id)
            .join(Role, Role.id == User.role_id)
            .join(Parent, Parent.user_id == User.id, isouter = True)
            .join(School, School.login_id == User.id, isouter = True)
            .join(Staff, Staff.login_id == User.id, isouter = True)
            .join(Doctor, Doctor.login_id == User.id, isouter = True)          
            .filter(
                CamperComment.camper_id == camper_id
            )
        ) 
        comments = db.execute(query)
        comments = comments.mappings().all()
        
        
    for comment in comments:
        final_comment = {}
        final_comment["id"] = comment["id"]
        final_comment["comment"] = comment["comment"]
        final_comment["author_role"] = comment["role_name"]
        
        if comment["parent_id"] is not None:
            final_comment["author"] = comment["tutor_name"] + " " + comment["tutor_lastname_father"] + " " + comment["tutor_lastname_mother"]
        if comment["staff_id"] is not None:
            final_comment["author"] = comment["staff_name"] + " " + comment["staff_lastname_father"] + " " + comment["staff_lastname_mother"]
        if comment["school_id"] is not None:
            final_comment["author"] = comment["school_name"]
        if comment["doctor_id"] is not None:
            final_comment["author"] = comment["doctor_name"] + " " + comment["doctor_lastname_father"] + " " + comment["doctor_lastname_mother"]
        data.append(final_comment)
    
    return data

def create_new_camper_comment(db, new_camper_comment: CamperCommentCreate):
    try:
        db_camper_comment = CamperComment(**new_camper_comment.dict())
        db.add(db_camper_comment)
        db.commit()
    except Exception as ex:
        return {"status": 3, "msg": "Internal server error"}
    return {"status": 1, "msg": "El comentario fue creado con exito"}


def update_camper_comment_by_id(
    db, camper_comment_id: int, modify_camper_comment: CamperCommentModify
):
    rows_updated = (
        db.query(CamperCommentModify)
        .filter_by(id=camper_comment_id)
        .update(modify_camper_comment, synchronize_session="fetch")
    )
    db.commit()
    return rows_updated


def get_camper_comment_by_camper_for_parent(db, camper_id: int):
    rows = (
        db.query(CamperComment)
        .filter(
            and_(
                CamperComment.camper_id == camper_id,
                CamperComment.is_public == True,
                CamperComment.show_to == 2,
            )
        )
        .all()
    )
    return rows

def get_all_camper_comments(db, camper_id: int):
    
    comments_query = (
        db.query(
            CamperComment.id,
            CamperComment.comment,
            CamperComment.camp_id,
            CamperComment.camper_id,
            CamperComment.is_public,
            CamperComment.show_to,
            CamperComment.user_id
        )
        .filter(
                CamperComment.camper_id == camper_id
        )
    )
    comments = db.execute(comments_query)
    comments = comments.mappings().all()
    camper_comments = []
    
    for comment in comments:
        comment_dict = dict(comment)
        user_id = comment["user_id"]
        user = (
        db.query(User)
        .filter(
            User.id == user_id
        ).first())    
        
        user_info = None
        
        if user.role_id == ROLE_PARENT_ID:
            user_info_query = (db.query(Parent.id, func.concat(Parent.tutor_name, ' ', Parent.tutor_lastname_father, ' ', Parent.tutor_lastname_mother).label('fullname'), Role.name.label("role")).select_from(Parent).join(User, User.id == Parent.user_id).join(Role, Role.id == User.role_id).filter(User.id == user.id))
            user_info = db.execute(user_info_query)
            user_info = user_info.mappings().first()
        if user.role_id == ROLE_STAFF_ID:
            user_info_query = (db.query(Staff.id, func.concat(Staff.name, ' ', Staff.lastname_father, ' ', Staff.lastname_mother).label('fullname'), Role.name.label("role"), Staff.coordinator).select_from(Staff).join(User, User.id == Staff.login_id).join(Role, Role.id == User.role_id).filter(User.id == user.id))
            user_info = db.execute(user_info_query)
            user_info = user_info.mappings().first()
        if user.role_id == ROLE_SCHOOL_ID:
            user_info_query = (db.query(School.id, School.name.label('fullname'), Role.name.label("role")).select_from(School).join(User, User.id == School.login_id).join(Role, Role.id == User.role_id).filter(User.id == user.id))
            user_info = db.execute(user_info_query)
            user_info = user_info.mappings().first()
        if user.role_id == ROLE_DOCTOR_ID:
            user_info_query = (db.query(Doctor.id,  func.concat(Doctor.name, ' ', Doctor.lastname_father, ' ', Doctor.lastname_mother).label('fullname'), Role.name.label("role")).select_from(Doctor).join(User, User.id == Doctor.login_id).join(Role, Role.id == User.role_id).filter(User.id == user.id))
            user_info = db.execute(user_info_query)
            user_info = user_info.mappings().first()
            
        comment_dict["comment_author"] = user_info
        camper_comments.append(comment_dict)

    return camper_comments


def get_camper_comment_by_camper_for_admin(db, camper_id: int):
    rows = (
        db.query(CamperComment)
        .filter(
            and_(
                CamperComment.camper_id == camper_id,
                CamperComment.is_public == True,
                CamperComment.show_to == ROLE_STAFF_ID,
                   
            )
        )
        .all()
    )
    return rows
def get_camper_comment_by_camper_for_school(db, camper_id: int):
    rows = (
        db.query(CamperComment)
        .filter(
            and_(
                CamperComment.camper_id == camper_id,
                CamperComment.is_public == True,
                CamperComment.show_to == ROLE_SCHOOL_ID,
            )
        )
        .all()
    )
    return rows
