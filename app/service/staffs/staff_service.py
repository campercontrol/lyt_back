from xmlrpc.client import boolean

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from crud.staffs.staff_crud import (
    get_all_prospect,
    search_all_prospect,
    get_all_staff,
    search_all_staff,
    create_new_prospect,
    create_complete_prospect,
    accept_prospect,
    delete_prospect,
    staff_dashboard,
    staff_camps,
    get_staff_by_id,
    update_staff_by_id,
    get_staff_band,
    get_staff_food_restriction,
    get_staff_vaccines,
    get_prospects_general_report,
    get_all_staff_report
)

from crud.catalogs.constant_crud import (
    get_all_blood_type_id_name,
    get_all_gender_id_name,
)

from crud.trophies.trophy_staff_crud import (
    get_trophy_by_staff,
    get_trophy_record_by_staff
)

from schema.staffs.staff_schema import (
    ProspectCompleteCreate,
    StaffModify,
    StaffComplete,
)
from schema.staff_catalogs.staff_vaccine_schema import StaffVaccineCreate, StaffVaccineModify
from schema.staff_catalogs.staff_food_restriction_schema import (
    StaffFoodRestrictionCreate,
    StaffFoodRestrictionModify
)

from crud.catalogs.food_restriction_crud import get_all_food_restriction
from crud.catalogs.vaccine_crud import get_all_vaccine
from crud.staff_catalogs.staff_vaccine_crud import (
    get_staff_vaccine_by_vaccine,
    create_new_staff_vaccine,
    update_staff_vaccine_by_id,
    get_staff_all_vaccines_by_staff_id
)

from crud.staff_catalogs.staff_food_restriction_crud import (
    get_staff_food_restriction_by_food_r,
    create_new_staff_food_restriction,
    update_staff_food_restriction_by_id,
    get_all_staff_food_restriction_by_id
)

from crud.camps.staff_in_camp_crud import (
    get_past_camp_confirmed_by_staff,
    get_future_camp_confirmed_by_staff,
    get_all_past_camp_by_staff,
    get_all_future_camp_by_staff
)

from crud.staffs.staff_comment_crud import (
    get_staff_comment_by_staff_for_admin
)
from crud.staffs.staff_record_crud import update_all_staff_record_status, update_staff_record_status
from utils.db import SessionLocal
from schema.pagination.pagination_schema import Pagination
from helper.pagination_helpers import pagination_params

staff_routes = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@staff_routes.get("/prospect/", tags=["Prospect"])
def get_prospects(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db)):
    list_prospect = get_all_prospect(db, pagination)
    return {"data": list_prospect}

@staff_routes.get("/search_prospect/", tags=["Prospect"])
def get_prospects(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db), name: Optional[str] = '', email: Optional[str] = ''):
    list_prospect = search_all_prospect(db, pagination, name, email)
    return {"data": list_prospect}

@staff_routes.get("/staff/", tags=["Staff"])
def get_staff(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db)):
    # update_all_staff_record_status(db)
    list_staff = get_all_staff(db, pagination)
    return {"data": list_staff}

@staff_routes.get("/search_staff/", tags=["Staff"])
def get_staff(pagination: Annotated[Pagination, Depends(pagination_params)], db: Session = Depends(get_db),  name: Optional[str] = '', lastname_mother: Optional[str] = '', lastname_father: Optional[str] = '', email: Optional[str] = ''):
    # update_all_staff_record_status(db)
    list_staff = search_all_staff(db, pagination, name, lastname_father, lastname_mother, email)
    return {"data": list_staff}


@staff_routes.post("/prospect/", tags=["Prospect"])
def create_prospect(
    new_prospect: ProspectCompleteCreate, db: Session = Depends(get_db)
):
    result = create_complete_prospect(db, new_prospect)
    
    if result == 2:
        return {"detail": {"status": 2, "msg": "Ya existe una cuenta con ese email"}} 
    if result == 3:
        return {"detail": {"status": 3, "msg": "Ocurrió un error al crear la cuenta del prospecto"}} 
    if result == 1: 
        return {"detail": {"status": 1, "msg": "El prospecto se creo correctamente"}} 



@staff_routes.patch("/accept_prospect/{prospect_id}", tags=["Prospect"])
def accept_prospecto_to_staff(prospect_id: int, db: Session = Depends(get_db)):
    status = accept_prospect(db, prospect_id)
    return {"data": status}


@staff_routes.delete("/delete_prospect/{prospect_id}", tags=["Prospect"])
def delete_prospect_by_id(prospect_id: int, db: Session = Depends(get_db)):
    status = delete_prospect(db, prospect_id)
    return {"status": status}


@staff_routes.get("/staff_dashboard/{staff_id}", tags=["Staff"])
def get_staff_dashboard(staff_id: int, db: Session = Depends(get_db)):
    staff_dashboard_info = staff_dashboard(db, staff_id)
    return {"data": staff_dashboard_info}

@staff_routes.get("/staff/{staff_id}/camps", tags=["Staff"])
def get_staff_camps(staff_id: int, db: Session = Depends(get_db)):
    response = staff_camps(db, staff_id)
    return {"data": response}


@staff_routes.get("/staff/{staff_id}", tags=["Staff"])
def get_staff_info(staff_id: int, db: Session = Depends(get_db)):
    staff = get_staff_by_id(db, staff_id)
    return {"data": staff}


@staff_routes.patch("/staff/{staff_id}", tags=["Staff"])
def update_staff(
    staff_id: str, modify_staff: StaffModify, db: Session = Depends(get_db)
):
    update_data = modify_staff.dict(exclude_unset=True)
    print(update_data)
    staff_update_result = update_staff_by_id(db, staff_id, update_data)

    if staff_update_result != 0:
        exist_staff = get_staff_by_id(db, staff_id)
        return {"mensaje": "Actualizado Correctamente", "data": exist_staff}
    else:
        return {"mensaje": "Ningun registro fue afectado", "data": ""}


@staff_routes.post("/staff/vaccine/", tags=["Staff"])
def create_staff_vaccine(
    new_staff_vaccine: StaffVaccineCreate, db: Session = Depends(get_db)
):
    staff_vaccine = create_new_staff_vaccine(db, new_staff_vaccine)
    return {"data": staff_vaccine}


@staff_routes.post("/staff/food_restriction/", tags=["Staff"])
def create_staff_food_restriction(
    new_staff_food_restriction: StaffFoodRestrictionCreate,
    db: Session = Depends(get_db),
):
    staff_food_restriction = create_new_staff_food_restriction(
        db, new_staff_food_restriction
    )
    return {"data": staff_food_restriction}


@staff_routes.patch("/staff/complete/{staff_id}", tags=["Staff"])
def update_staff_complete(staff_id:str,modify_staff:StaffComplete,db: Session = Depends(get_db)):

    update_data= modify_staff.dict(exclude_unset=True)
    staff_update_result = update_staff_by_id(db, staff_id, update_data["staff"])

    for vaccine in update_data["vaccines"]:
        s_vaccine = get_staff_vaccine_by_vaccine(db, vaccine["id"])
        print("#######################")
        print(vaccine)
        #print(vaccine["is_active"])
        if s_vaccine:
            staff_vaccine = StaffVaccineModify(
                staff_id=staff_id,
                vaccine_id=vaccine['id'],
                is_active=vaccine["is_active"],
            ).dict(exclude_unset=True)
            update_staff_vaccine_by_id(db, vaccine['id'], staff_id, staff_vaccine)
        else: 
            staff_vaccine = StaffVaccineCreate(
                staff_id=staff_id,
                vaccine_id=vaccine['id'],
                is_active=vaccine["is_active"],
            )
            create_new_staff_vaccine(db, staff_vaccine)

    for food_restriction in update_data["food_restrictions"]:
        s_food_restriction = get_staff_food_restriction_by_food_r(db, food_restriction["id"])
        if s_food_restriction:
            staff_food_restriction = StaffFoodRestrictionModify(
                staff_id=staff_id,
                food_restriction_id=food_restriction["id"],
                is_active=food_restriction["is_active"],
            ).dict(exclude_unset=True)
            update_staff_food_restriction_by_id(db, food_restriction["id"], staff_id, staff_food_restriction)
        else: 
            staff_food_restriction = StaffFoodRestrictionCreate(
                staff_id=staff_id,
                food_restriction_id=food_restriction["id"],
                is_active=food_restriction["is_active"],
            )
            create_new_staff_food_restriction(db, staff_food_restriction)

    if update_staff_complete != 0:
        exist_staff = get_staff_by_id(db, staff_id)
        return {"mensaje": "Actualizado Correctamente", "data": exist_staff}
    else:
        return {"mensaje": "Ningun registro fue afectado", "data": ""}


@staff_routes.get("/staff/complete/{staff_id}/{language}", tags=["Staff"])
def get_staff_complete(staff_id: int, language: str, db: Session = Depends(get_db)):
    genders = get_all_gender_id_name(db, language)
    blood_type = get_all_blood_type_id_name(db, language)
    staff = get_staff_by_id(db, staff_id)
    staff_vaccines = get_staff_vaccines(db, staff_id)
    staff_food_restriction = get_staff_food_restriction(db, staff_id)

    return {
        "staff": staff,
        "genders": genders,
        "blood_types": blood_type,
        "vaccines": staff_vaccines,
        "food_restrictions": staff_food_restriction,
    }


@staff_routes.get("/staff/profile/{staff_id}/{language}", tags=["Staff"])
def get_staff_profile(staff_id: int, language: str, db: Session = Depends(get_db)):
    
    staff_past_camps = get_all_past_camp_by_staff(db, staff_id)
    staff_upcoming_camps = get_all_future_camp_by_staff(db, staff_id)
    staff_band = get_staff_band(db, staff_id)
    staff_profile = get_staff_by_id(db, staff_id)
    staff_comments = get_staff_comment_by_staff_for_admin(db, staff_id)
    staff_trophy_records = get_trophy_record_by_staff(db, staff_id) 
    staff_trophy = get_trophy_by_staff(db,staff_id)
    return{
        "staff_band": staff_band[0],
        "staff_trophy_records": staff_trophy_records,
        "staff_profile": staff_profile,
        "staff_past_camps": staff_past_camps,
        "staff_upcoming_camps": staff_upcoming_camps,
        "staff_comments": staff_comments,
        "staff_trophies": staff_trophy
    }
    
    
@staff_routes.post("/staff_record_status", tags=["Staff"])
def staff_record_status(db: Session = Depends(get_db)):
    result = update_staff_record_status(db, 22881)
    return result
    
@staff_routes.post("/prospects/report/general", tags=["Staff"])
def prospects_general_report(db: Session = Depends(get_db)):
    report = get_prospects_general_report(db)
    return report
    
@staff_routes.get("/staff/report/general", tags=["Staff"])
def staff_general_report(db: Session = Depends(get_db)):
    report = get_all_staff_report(db)
    return report
    