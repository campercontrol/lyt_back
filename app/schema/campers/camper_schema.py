from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from xmlrpc.client import boolean

from schema.catalogs.vaccine_schema import VaccineCreate

from pydantic import BaseModel, Field

class CamperCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name:str = Field(
        title="Nombre"
    )
    lastname_father:str = Field(
        title="Primer apellido"
    )
    lastname_mother:Optional[str] = Field(
        title="Segundo apellido"
    )    
    photo:str = Field(
        title="Foto"
    )    
    gender_id:int = Field(
        title="Genero"
    )
    birthday:date = Field(
        title="Fecha de nacimiento"
    )
    height:float = Field(
        title="Altura"
    )
    weight:float = Field(
        title="Peso"
    )
    grade:int = Field(
        title="Grado escolar"
    )
    school_id:int = Field(
        title="Escuela"
    )
    school_other:Optional[str] = Field(
        title="Otra Escuela"
    )
    email:str = Field(
        title="Email"
    )
    can_swim:int = Field(
        title="¿Sabe nadar?"
    )
    affliction:str = Field(
        title="Enfermedades"
    )
    blood_type:int = Field(
        title="Tipo de sangre"
    )
    heart_problems:str = Field(
        title="Problemas cardiacos"
    )
    psicology_treatments:str = Field(
        title="Tratamientos psicologicos o psiquiatricos"
    )
    prevent_activities:str = Field(
        title="Cirugias, fracturas o esguinces que le impiden realizar actividad fisica"
    )
    drug_allergies:str = Field(
        title="Alergia a medicamentos"
    )
    other_allergies:str = Field(
        title="Otras alergias"
    )
    nocturnal_disorders:str = Field(
        title="Alteraciones nocturnas"
    )
    phobias:str = Field(
        title="Fobias o miedos"
    )
    drugs:str = Field(
        title="Medicamentos que tomara durante el camp"
    )
    doctor_precall:boolean = Field(
        title="Llamada previa del doctor"
    )
    prohibited_foods:str = Field(
        title="Comida prohibida"
    )
    comments_admin:Optional[str] = Field(
        title="Comentarios del administrador"
    )
    insurance:Optional[boolean] = Field(
        title="Seguro medico"
    )
    insurance_company:Optional[str] = Field(
        title="Compañia de seguro"
    )
    insurance_number:Optional[str] = Field(
        title="Numero de seguro"
    )
    security_social_number:Optional[str] = Field(
        title="Numero de seguro social"
    )
    contact_name:str = Field(
        title="Nombre del contacto de emergencia"
    )
    contact_relation:str = Field(
        title="Relación con el contacto de emergencia"
    )
    contact_homephone:str = Field(
        title="Telefono del contacto de emergencia"
    )
    contact_cellphone:str = Field(
        title="Celular del contacto de emergencia"
    )
    parent_id:int = Field(
        title="Titular de la cuenta"
    )
    # record_id:int = Field(
    #     title="Record de campamentos del camper"
    # )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class CamperModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title="Nombre"
    )
    lastname_father:str = Field(
        title="Primer apellido"
    )
    lastname_mother:Optional[str] = Field(
        title="Segundo apellido"
    )    
    photo:str = Field(
        title="Foto"
    )    
    gender_id:int = Field(
        title="Genero"
    )
    birthday:date = Field(
        title="Fecha de nacimiento"
    )
    height:float = Field(
        title="Altura"
    )
    weight:float = Field(
        title="Peso"
    )
    grade:int = Field(
        title="Grado escolar"
    )
    school_id:int = Field(
        title="Escuela"
    )
    school_other:Optional[str] = Field(
        title="Otra Escuela"
    )
    email:str = Field(
        title="Email"
    )
    can_swim:int = Field(
        title="¿Sabe nadar?"
    )
    affliction:str = Field(
        title="Enfermedades"
    )
    blood_type:int = Field(
        title="Tipo de sangre"
    )
    heart_problems:str = Field(
        title="Problemas cardiacos"
    )
    psicology_treatments:str = Field(
        title="Tratamientos psicologicos o psiquiatricos"
    )
    prevent_activities:str = Field(
        title="Cirugias, fracturas o esguinces que le impiden realizar actividad fisica"
    )
    drug_allergies:str = Field(
        title="Alergia a medicamentos"
    )
    other_allergies:str = Field(
        title="Otras alergias"
    )
    nocturnal_disorders:str = Field(
        title="Alteraciones nocturnas"
    )
    phobias:str = Field(
        title="Fobias o miedos"
    )
    drugs:str = Field(
        title="Medicamentos que tomara durante el camp"
    )
    doctor_precall:boolean = Field(
        title="Llamada previa del doctor"
    )
    prohibited_foods:str = Field(
        title="Comida prohibida"
    )
    comments_admin:Optional[str] = Field(
        title="Comentarios del administrador"
    )
    insurance:Optional[str] = Field(
        title="Seguro medico"
    )
    insurance_company:Optional[str] = Field(
        title="Compañia de seguro"
    )
    insurance_number:Optional[str] = Field(
        title="Numero de seguro"
    )
    security_social_number:Optional[str] = Field(
        title="Numero de seguro social"
    )
    contact_name:str = Field(
        title="Nombre del contacto de emergencia"
    )
    contact_relation:str = Field(
        title="Relación con el contacto de emergencia"
    )
    contact_homephone:str = Field(
        title="Telefono del contacto de emergencia"
    )
    contact_cellphone:str = Field(
        title="Celular del contacto de emergencia"
    )
    parent_id:int = Field(
        title="Titular de la cuenta"
    )
    record_id:int = Field(
        title="Record de campamentos del camper"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class CamperCatalog(BaseModel):
    id: int
    name: str
    is_active: boolean

class CamperComplete(BaseModel):

    camper: CamperCreate
    vaccines: Optional[list[CamperCatalog]]
    food_restrictions: Optional[list[CamperCatalog]]
    licensed_medicines: Optional[list[CamperCatalog]]
    pathological_background: Optional[list[CamperCatalog]]
    pathological_background_fm: Optional[list[CamperCatalog]]


## Falta agregar max_lenght