from xmlrpc.client import boolean
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, HTTPException
#from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session, add_mapped_attribute
from typing import List
from schema.pagination.pagination_schema import Pagination
from helper.pagination_helpers import pagination_params

from crud.catalogs.constant_crud import (
    get_all_blood_type_id_name,
    get_all_gender_id_name,
    get_all_grade_id_name,
)
from crud.catalogs.vaccine_crud import get_all_vaccine_id_name
from crud.campers_catalogs.camper_vaccine_crud import (
    create_new_camper_vaccine,
    update_camper_vaccine_by_ids,
)
from crud.catalogs.food_restriction_crud import get_all_food_restriction_id_name
from crud.catalogs.licensed_medicine_crud import get_all_licensed_medicine_id_name
from crud.catalogs.pathological_background_crud import (
    get_all_pathological_background_id_name,
)
from crud.catalogs.pathological_background_family_crud import (
    get_all_pathological_background_family_id_name,
)
from crud.campers_catalogs.camper_food_restriction_crud import (
    create_new_camper_food_restriction,
    update_camper_food_restriction_by_ids,
)
from crud.campers_catalogs.camper_licensed_medicine_crud import (
    create_new_camper_licensed_medicine,
    update_camper_licensed_medicine_by_ids,
)
from crud.campers_catalogs.camper_pathological_background_crud import (
    create_new_camper_pathological_background,
    update_camper_pathological_background_by_ids,
)
from crud.campers_catalogs.camper_pathological_background_fm_crud import (
    create_new_camper_pathological_background_fm,
    update_camper_pathological_background_fm_by_ids,
)
from crud.campers.camper_crud import (
    get_all_camper,
    get_all_camper_admin,
    get_camper_by_uuid,
    create_new_camper,
    update_camper_by_id,
    get_vaccine_by_camper,
    get_licensed_medicine_by_camper,
    get_food_restriction_by_camper,
    get_pathological_background_by_camper,
    get_pathological_background_fm_by_camper,
    get_campers_from_parent,
    get_camper_band,
    search_camper_by_name_user,
    search_all_camper_admin,
    delete_camper,
    get_parent_campers_by_parent_id
)
from crud.campers.parent_crud import get_parent_by_uuid
from crud.campers.camper_comment_crud import get_all_camper_comments
from crud.camps.camp_crud import get_school_camp_for_camper, get_summer_camp_for_camper
from crud.camps.camper_in_camp_crud import (
    get_subscribe_by_camper,
    get_cancelled_by_camper,
    get_past_subscribe_by_camper,
    get_camps_name_amount_camper
)
from crud.crud_user import get_user_by_uuid
from crud.campers.school_crud import get_active_school
from schema.campers_catalogs.camper_vaccine_schema import (
    CamperVaccineCreate,
    CamperVaccineModify,
)
from schema.campers_catalogs.camper_food_restriction_schema import (
    CamperFoodRestrictionCreate,
    CamperFoodRestrictionModify,
)
from schema.campers_catalogs.camper_licensed_medicine_schema import (
    CamperLicensedMedicineCreate,
    CamperLicensedMedicineModify,
)
from schema.campers_catalogs.camper_pathological_background_schema import (
    CamperPathologicalBackCreate,
    CamperPathologicalBackModify,
)
from schema.campers_catalogs.camper_pathological_background_fm_schema import (
    CamperPathologicalBackFmCreate,
    CamperPathologicalBackFmModify,
)

from schema.campers.camper_schema import CamperCreate, CamperModify, CamperComplete
from utils.db import SessionLocal
from utils.payments.payment_table import get_camper_total_balance, get_camper_balance_per_camp
# from utils.image_tools import rewrite_image

from utils.db import db_mapping_rows_to_dict

camper_routes = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@camper_routes.get("/camper/", tags=["Campers"])
def get_camper(db: Session = Depends(get_db)):
    list_camper = get_all_camper(db)
    return {"data": list_camper}


@camper_routes.get("/camper/{camper_id}", tags=["Campers"])
def get_camper_by_id(camper_id: str, db: Session = Depends(get_db)):
    list_camper = get_camper_by_uuid(db, camper_id)
    return {"data": list_camper}


@camper_routes.get("/camper_complete/{camper_id}/{language}", tags=["Campers"])
def get_camper_by_id_complete(
    camper_id: str, language: str, db: Session = Depends(get_db)
):
    genders = get_all_gender_id_name(db, language)
    blood_type = get_all_blood_type_id_name(db, language)
    schools = (get_active_school(db),)
    grades = get_all_grade_id_name(db, language)
    list_camper = get_camper_by_uuid(db, camper_id)
    vaccines = get_vaccine_by_camper(db, camper_id)
    licensed_medicines = get_licensed_medicine_by_camper(db, camper_id)
    food_restrictions = get_food_restriction_by_camper(db, camper_id)
    pathological_backgrounds = get_pathological_background_by_camper(db, camper_id)
    pathological_backgrounds_family = get_pathological_background_fm_by_camper(
        db, camper_id
    )
    data = {
        "camper": list_camper,
        "vaccines": vaccines,
        "licensed_medicines": licensed_medicines,
        "food_restrictions": food_restrictions,
        "pathological_background": pathological_backgrounds,
        "pathological_background_fm": pathological_backgrounds_family,
        "genders": genders,
        "blood_types": blood_type,
        "school": schools,
        "grades": grades,
    }
    return data


@camper_routes.post("/camper/", tags=["Campercamper_schema"])
def create_camper(camper_complete: CamperComplete, db: Session = Depends(get_db)):
    new_camper = create_new_camper(db, camper_complete)
    # new_camper_id = getattr(new_camper, "id")
    # tmp_path_photo = getattr(new_camper, "photo")
    # final_path_photo = str(
    #    getattr(new_camper, "id")
    #    + getattr(new_camper, "name")
    #    + getattr(new_camper, "lastname_father")
    # )
    # rewrite_image(tmp_path_photo, final_path_photo)
    return {"camper_id": new_camper.id}


@camper_routes.patch("/camper/{camper_id}", tags=["Campers"])
def update_camper(
    camper_id: int, modify_camper: CamperComplete, db: Session = Depends(get_db)
):
    update_data = modify_camper.dict(exclude_unset=True)
    print(update_data)
    camper_upcdate_result = update_camper_by_id(db, camper_id, update_data["camper"])

    for vaccine in update_data["vaccines"]:
        camper_vaccine = CamperVaccineModify(
            camper_id=camper_id,
            vaccine_id=vaccine["id"],
            is_active=vaccine["is_active"],
        ).dict(exclude_unset=True)
        update_camper_vaccine_by_ids(db, vaccine["id"], camper_id, camper_vaccine)

    for food_restriction in update_data["food_restrictions"]:
        camper_food_restriction = CamperFoodRestrictionModify(
            camper_id=camper_id,
            food_restriction_id=food_restriction["id"],
            is_active=food_restriction["is_active"],
        ).dict(exclude_unset=True)
        update_camper_food_restriction_by_ids(
            db, food_restriction["id"], camper_id, camper_food_restriction
        )

    for licensed_medicine in update_data["licensed_medicines"]:
        camper_licensed_medicine = CamperLicensedMedicineModify(
            camper_id=camper_id,
            licensed_medicine_id=licensed_medicine["id"],
            is_active=licensed_medicine["is_active"],
        ).dict(exclude_unset=True)
        update_camper_licensed_medicine_by_ids(
            db, licensed_medicine["id"], camper_id, camper_licensed_medicine
        )

    for pathological_back in update_data["pathological_background"]:
        camper_pathological_back = CamperPathologicalBackModify(
            camper_id=camper_id,
            pathological_background_id=pathological_back["id"],
            is_active=pathological_back["is_active"],
        ).dict(exclude_unset=True)
        update_camper_pathological_background_by_ids(
            db, pathological_back["id"], camper_id, camper_pathological_back
        )

    for pathological_back_fm in update_data["pathological_background_fm"]:
        camper_pathological_back = CamperPathologicalBackFmModify(
            camper_id=camper_id,
            pathological_background_family_id=pathological_back_fm["id"],
            is_active=pathological_back_fm["is_active"],
        ).dict(exclude_unset=True)
        update_camper_pathological_background_fm_by_ids(
            db, pathological_back_fm["id"], camper_id, camper_pathological_back
        )

    if camper_upcdate_result != 0:
        exist_camper = get_camper_by_uuid(db, camper_id)
        return {"mensaje": "Actualizado Correctamente", "data": exist_camper}
    else:
        return {"mensaje": "Ningun registro fue afectado", "data": ""}


@camper_routes.get("/camper/{camper_id}/vaccines/")
def get_vaccine_by_camper_id(camper_id: int, db: Session = Depends(get_db)):
    list_vaccine = get_vaccine_by_camper(db, camper_id)
    return {"data": list_vaccine}


@camper_routes.get("/camper_form/{language}")
def get_camperform(language: str, db: Session = Depends(get_db)):
    genders = get_all_gender_id_name(db, language)
    blood_type = get_all_blood_type_id_name(db, language)
    schools = get_active_school(db)
    grades = get_all_grade_id_name(db, language)
    vaccines = get_all_vaccine_id_name(db)
    for x in range(0, len(vaccines)):
        vaccines[x] = dict(vaccines[x])
        vaccines[x]["is_active"] = False

    licensed_medicines = get_all_licensed_medicine_id_name(db)
    for x in range(0, len(licensed_medicines)):
        licensed_medicines[x] = dict(licensed_medicines[x])
        licensed_medicines[x]["is_active"] = False

    food_restrictions = get_all_food_restriction_id_name(db)
    for x in range(0, len(food_restrictions)):
        food_restrictions[x] = dict(food_restrictions[x])
        food_restrictions[x]["is_active"] = False

    pathological_backgrounds = get_all_pathological_background_id_name(db)
    for x in range(0, len(pathological_backgrounds)):
        pathological_backgrounds[x] = dict(pathological_backgrounds[x])
        pathological_backgrounds[x]["is_active"] = False

    pathological_backgrounds_family = get_all_pathological_background_family_id_name(db)
    for x in range(0, len(pathological_backgrounds_family)):
        pathological_backgrounds_family[x] = dict(pathological_backgrounds_family[x])
        pathological_backgrounds_family[x]["is_active"] = False

    data = {
        "camper": {
            "name": "string",
            "lastname_father": "string",
            "lastname_mother": "string",
            "photo": "string",
            "gender_id": 0,
            "birthday": "2023-04-11",
            "height": 0,
            "weight": 0,
            "grade": 0,
            "school_id": 0,
            "school_other": "string",
            "email": "string",
            "can_swim": 0,
            "affliction": "string",
            "blood_type": 0,
            "heart_problems": "string",
            "psicology_treatments": "string",
            "prevent_activities": "string",
            "drug_allergies": "string",
            "other_allergies": "string",
            "nocturnal_disorders": "string",
            "phobias": "string",
            "drugs": "string",
            "doctor_precall": True,
            "prohibited_foods": "string",
            "comments_admin": "string",
            "insurance": True,
            "insurance_company": True,
            "insurance_number": "string",
            "security_social_number": "string",
            "contact_name": "string",
            "contact_relation": "string",
            "contact_homephone": "string",
            "contact_cellphone": "string",
            "record_id": 1,
            "parent_id": 1,
        },
        "genders": genders,
        "blood_types": blood_type,
        "school": schools,
        "grades": grades,
        "vaccines": vaccines,
        "licensed_medicines": licensed_medicines,
        "food_restrictions": food_restrictions,
        "pathological_background": pathological_backgrounds,
        "pathological_background_fm": pathological_backgrounds_family,
    }
    return data


@camper_routes.get("/campers_from_parent/{parent_id}", tags=["Campers"])
def get_campers_by_parent_id(parent_id: int, db: Session = Depends(get_db)):
    list_camps = []
    list_camper = get_campers_from_parent(db, parent_id)
    for camper in list_camper:
        camps = get_subscribe_by_camper(db, camper.id)
        if len(camps) != 0:
            list_camps.append(camps)
    data = {"list_campers": list_camper, "list_camps": list_camps}
    return data


@camper_routes.get("/camper_band/{camper_id}", tags=["Campers"])
def get_camper_info_band(camper_id: int, db: Session = Depends(get_db)):
    camper_band = get_camper_band(db, camper_id)
    return {"data": camper_band}


@camper_routes.get("/camper_dashboard/{camper_id}", tags=["Campers"])
def get_camper_dashboard(camper_id: int, db: Session = Depends(get_db)):
    camper_band = get_camper_band(db, camper_id)

    camper_subscribe_camps = get_subscribe_by_camper(db, camper_id)
    camper_cancelled_camps = get_cancelled_by_camper(db, camper_id)
    camper_passed_camps = get_past_subscribe_by_camper(db, camper_id)

    camp_ids = []
    for camper_in_camp in camper_subscribe_camps:
        camp_ids.append(camper_in_camp["camp_id"])

    # for camper_in_camp in camper_cancelled_camps:
    #     camp_ids.append(camper_in_camp["camp_id"])

    for camper_in_camp in camper_passed_camps:
        camp_ids.append(camper_in_camp["camp_id"])

    camper_school = get_school_camp_for_camper(db, camper_id)
    camper_summer = get_summer_camp_for_camper(db, camper_id)

    camper_school_final = [d for d in camper_school if d["camp_id"] not in camp_ids]
    camper_summer_final = [d for d in camper_summer if d["camp_id"] not in camp_ids]

    data = {
        "camper_band": camper_band,
        "available_school_camps": camper_school_final,
        "summer_school_camps": camper_summer_final,
        "subscribe_camps": camper_subscribe_camps,
        "cancelled_camps": camper_cancelled_camps,
        "passed_camps": camper_passed_camps,
    }
    return data


@camper_routes.get("/camper_profile/{camper_id}", tags=["Campers"])
def get_camper_profile(camper_id: int, db: Session = Depends(get_db)):
    camper_band = get_camper_band(db, camper_id)
    camper_info = get_camper_by_id_complete(camper_id, "es", db)
    parent = get_parent_by_uuid(db, camper_info["camper"].parent_id)
    user = get_user_by_uuid(db, parent.user_id)
    camper_comments = get_all_camper_comments(db, camper_id)
    camper_subscribe_camps = get_subscribe_by_camper(db, camper_id)
    camper_cancelled_camps = get_cancelled_by_camper(db, camper_id)
    camper_passed_camps = get_past_subscribe_by_camper(db, camper_id)
    siblings = get_parent_campers_by_parent_id(db, parent.id) 
    filtered_siblings = [sibling for sibling in siblings if sibling.id != camper_id]


    camper_total_balance = get_camper_total_balance(db, camper_id)
    
    for index, camper_passed_camp in enumerate(camper_passed_camps):
        camper_passed_camp_dict = dict(camper_passed_camp)
        camper_passed_camp_dict["camper_payment_balance"] = get_camper_balance_per_camp(db, camper_id, camper_passed_camp["camp_id"])
        camper_passed_camps[index] = camper_passed_camp_dict
    
    for index, camper_subscribe_camp in enumerate(camper_subscribe_camps):
        camper_subscribe_camps_dict = dict(camper_subscribe_camp)
        camper_subscribe_camps_dict["camper_payment_balance"] = get_camper_balance_per_camp(db, camper_id, camper_subscribe_camp["camp_id"])
        camper_subscribe_camps[index] = camper_subscribe_camps_dict
    
    for index, camper_cancelled_camp in enumerate(camper_cancelled_camps):
        camper_cancelled_camps_dict = dict(camper_cancelled_camp)
        camper_cancelled_camps_dict["camper_payment_balance"] = get_camper_balance_per_camp(db, camper_id, camper_cancelled_camp["camp_id"])
        camper_cancelled_camps[index] = camper_cancelled_camps_dict

    data = {
        "camper_band": camper_band,
        "camper_info": camper_info,
        "camper_total_amount": camper_total_balance,
        "parent": parent,
        "siblings": filtered_siblings,
        "user_email": user[0].email,
        "camper_comments": camper_comments,
        "camper_subscribe_camps": camper_subscribe_camps,
        "camper_cancelled_camps": camper_cancelled_camps,
        "camper_passed_camps": camper_passed_camps,
    }
    return data

@camper_routes.delete("/delete_camper/{camper_id}", tags=["Campers"])
def delete_camper_by_id(camper_id:int, db: Session = Depends(get_db)):
    response = delete_camper(db, camper_id)
    if response == None:
        raise HTTPException(status_code=404, detail="Camper not found")

    if response['status'] == 3:
         raise HTTPException(status_code=500, detail=response)
    return {"detail": response}    

@camper_routes.get("/search/camper/{search}", tags=["Campers"])
def get_search_camper(search:str, db: Session = Depends(get_db)):
    possible_campers  = search_camper_by_name_user(db, search)
    return { "data": possible_campers }

@camper_routes.get("/admin/camper/", tags=["Campers"])
def get_admin_camper(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db)):
    campers = get_all_camper_admin(db, pagination)
    return { "data": campers }


@camper_routes.get("/admin/search_camper/", tags=["Campers"])
def get_admin_camper(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db), camper_name: Optional[str] = '', camper_lastname_father: Optional[str] = '',camper_lastname_mother: Optional[str] = '', tutor_1_name: Optional[str] = '',tutor_1_lastname_father: Optional[str] = '', tutor_1_lastname_mother: Optional[str] = '', tutor_1_email: Optional[str] = '', tutor_2_name: Optional[str] = '', tutor_2_lastname_father: Optional[str] = '',tutor_2_lastname_mother: Optional[str] = '', tutor_2_email: Optional[str] = ''):
    campers = search_all_camper_admin(db, pagination, camper_name,camper_lastname_father, camper_lastname_mother, tutor_1_name, tutor_1_lastname_father, tutor_1_lastname_mother, tutor_1_email, tutor_2_name, tutor_2_lastname_father,tutor_2_lastname_mother, tutor_2_email)
    return { "data": campers }