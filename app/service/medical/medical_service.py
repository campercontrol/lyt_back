from xmlrpc.client import boolean

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud.camps.camp_crud import get_camp_by_id
from crud.camps.camper_in_camp_crud import get_campers_for_camp
from crud.camps.staff_in_camp_crud import get_staff_in_camp
from crud.camps.location_crud import get_location_by_uuid
from crud.medical.camper_visit_crud import (
    camper_visit_triage_for_camp,
    camper_visit_for_camp,
    create_new_camper_visit,
    update_medical_camper_visit
)
from crud.medical.staff_visit_crud import staff_visit_triage_for_camp
from crud.campers.parent_crud import get_parent_for_admin_by_id, get_parent_by_uuid, get_parent_by_camper_id
from crud.campers.camper_crud import get_camper_by_uuid
from service.campers.camper_service import get_camper_by_id_complete
from crud.staffs.staff_crud import get_staff_by_id
from crud.catalogs.constant_crud import get_all_triage

from schema.medical.camper_visit_schema import CamperVisitCreate, CamperVisitModify

from utils.db import SessionLocal

medical_routes = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@medical_routes.get("/medical/camp/{camp_id}", tags=["Medical"])
def get_medical_camp(camp_id: int, db: Session = Depends(get_db)):
    camp_info = get_camp_by_id(db, camp_id)
    campers = get_campers_for_camp(db, camp_id)
    staffs = get_staff_in_camp(db, camp_id)
    location = get_location_by_uuid(db, camp_info.location_id)
    campers_medical = []
    for camper_in_camp in campers:
        camper = get_camper_by_uuid(db, camper_in_camp["camper_id"])
        # print("camper")
        # print(camper.parent_id)
        tutor = get_parent_for_admin_by_id(db, camper.parent_id)
        camper_triages = camper_visit_triage_for_camp(db, camper.id, camp_id)

        if tutor != "Parent doesn't exist":
        
            camper_complete = {
                "camper_id": camper.id,
                "camper_name": camper_in_camp["camper_full_name"],
                "camper_photo": camper.photo,
                "medical_triages": camper_triages,
                "tutor_fullname": camper_in_camp["tutor_full_name"],
                "tutor_email": camper_in_camp["tutor_email"],
                "tutor_cellphone": tutor.tutor_cellphone,
                "second_tutor_full_name": camper_in_camp["second_tutor_full_name"],
                "second_tutor_email": camper_in_camp["second_tutor_email"],
                "second_tutor_cellphone": tutor.contact_cellphone,
            }
            # print(camper_complete)
            campers_medical.append(camper_complete)
    staffs_medical = []
    for staff_in_camp in staffs:
        staff = get_staff_by_id(db, staff_in_camp.staff_id)
        staff_triages = staff_visit_triage_for_camp(db, staff_in_camp.staff_id, camp_id)
        staff_complete = {
            "staff_id": staff_in_camp.staff_id,
            "staff_photo": staff_in_camp.staff_photo,
            "staff_full_name": staff_in_camp.staff_full_name,
            "staff_email": staff_in_camp.staff_email,
            "staff_cellphone": staff.cellphone,
            "staff_home_phone": staff.home_phone,
            "staff_contact_name": staff.staff_contact_name,
            "staff_contact_relation": staff.staff_contact_relation,
            "staff_contact_homephone": staff.staff_contact_homephone,
            "staff_contact_cellphone": staff.staff_contact_cellphone,
            "medical_triages": staff_triages
        }
        staffs_medical.append(staff_complete)
    return {
        "camp_info": camp_info,
        "campers": campers_medical,
        "location": location,
        "staffs": staffs_medical,
    }


@medical_routes.get("/medical/camp/{camp_id}/camper/{camper_id}", tags=["Medical"])
def get_medical_camp_camper(
    camp_id: int, camper_id: int, db: Session = Depends(get_db)
):
    camper_visits = camper_visit_for_camp(db, camper_id, camp_id)
    camper_info = (camper_id, "es", db)
    camper = camper_info["camper"]
    camper_parent = get_parent_by_camper_id(db, camper.id)
    parent_info = get_parent_by_uuid(db, camper_parent["id"])
    return {
        "camper_visits": camper_visits,
        "camper_info": camper_info,
        "parent_info": parent_info,
    }


@medical_routes.get("/medical/camper/visit/form/{camper_id}", tags=["Medical"])
def get_medical_camper_visit_form(camper_id: int, db: Session = Depends(get_db)):
    triage_options = get_all_triage(db)
    camper_info = get_camper_by_id_complete(camper_id, "es", db)
    camper = camper_info["camper"]
    parent_info = get_parent_by_uuid(db, camper.id)
    med_auth = [
        "Preautorización en sistema de registro",
        "Se contacta a tutores",
        "Por parte de la Escuela / Maestras",
        "Por parte de Camper Control (In Loco Parentis)",
        "No se administraron medicamentos",
    ]   
    return {
        "triage": triage_options,
        "medicine_auth": med_auth,
        "camper_info": camper_info,
        "parent_info": parent_info,
    }

@medical_routes.post("/medical/camper/visit/", tags=["Medical"])
def create_medical_camper_visit(camper_visit: CamperVisitCreate, db: Session = Depends(get_db)):
    response =  create_new_camper_visit(db, camper_visit)

    if response['status'] == 3 or response['status'] == 2 :
        raise HTTPException(status_code=500, detail= response['detail'])
    return response

@medical_routes.patch("/medical/camper/visit/{visit_id}", tags=["Medical"])
def upd_medical_camper_visit(camper_visit: CamperVisitModify, visit_id: int, db: Session = Depends(get_db)):
    response = update_medical_camper_visit(db,camper_visit, visit_id)
    return {"detail": {"status": 1, "msg": "Medical Visit Updated Successfully", "data": response}}