from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from schema.user import UserCreate

from pydantic import BaseModel, Field, AnyUrl, condecimal

class ProspectCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    login_id: Optional[int] = Field(
        title= "Usuario"
    ) 
    name: str = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    lastname_father: str = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    lastname_mother: Optional[str] = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    gender_id: int = Field(
        title="Genero"
    )
    birthday: date = Field(
        title="Fecha de nacimiento"
    )
    curp: str = Field(
        title= "CURP",
        max_lenght= 25       
    )
    bio: str= Field(
        title= "Biografia"
    )
    cv : str = Field(
        title= "Curriculum"
    )
    photo: str = Field(
        title= "Fotografía"
    )
    cellphone: str = Field(
        title="Celular",
        max_lenght=20
    )
    home_phone: str = Field(
        title="Telefono de casa",
        max_lenght=20
    )
    facebook: str = Field(
        title="Facebook",
        max_lenght=25
    )
    coordinator: Optional[bool] = Field(
        title="Coordinador",
        default=False
    )
    employee: bool = Field(
        title="empleado",
        default=False
    )
    employee_email_send: bool = Field( 
        title="correo de activacion",
        default=False
    )
    season_id: int = Field( 
        title="temporada",
        default=1   
    )
    record_id: Optional[int] = Field(
        title="record",
        default=1
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class ProspectCompleteCreate(BaseModel):
    user: UserCreate
    prospect : ProspectCreate


class StaffModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    login_id: Optional[int] = Field(
        title= "Usuario"
    ) 
    name: str = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    lastname_father: str = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    lastname_mother: Optional[str] = Field(
        title= "Numero de transacción",
        max_lenght= 50       
    )
    gender_id: int = Field(
        title="Genero"
    )
    birthday: date = Field(
        title="Fecha de nacimiento"
    )
    affliction: str = Field(
        title = "Enfermedades que padece"
    )
    curp: str = Field(
        title= "CURP",
        max_lenght= 25       
    )
    rfc: str = Field(
        title= "RFC"
    )
    bio: str= Field(
        title= "Biografia"
    )
    cv : str = Field(
        title= "Curriculum"
    )
    photo: str = Field(
        title= "Fotografía"
    )
    cellphone: str = Field(
        title="Celular",
        max_lenght=20
    )
    home_phone: str = Field(
        title="Telefono de casa",
        max_lenght=20
    )
    blood_type : str = Field(
        title="Tipo de sangre"
    )
    drug_allergies: str = Field(
        title = "Alergia a medicamentos"
    )
    other_allergies: str = Field(
        title = "Otras alergias"
    )
    nocturnal_disorders: str = Field(
        title = "Problemas nocturnos"
    )
    phobias: str = Field(
        title = "Fobias o miedos"
    )
    drugs: str = Field(
        title = "Durante el campamento, ¿Estará tomando algún medicamento?"
    )
    prohibited_foods: str = Field(
        title = "Comida prohibida"
    )
    staff_contact_name: str = Field(
        title="Nombre de contacto"
    )
    staff_contact_relation: str = Field(
        title="Relacion con la persona de contacto"
    )
    staff_contact_homephone: str = Field(
        title="Telefono de casa de contacto"
    )
    staff_contact_cellphone: str = Field(
        title="Telefono celular de contacto"
    )
    facebook: str = Field(
        title="Facebook",
        max_lenght=25
    )
    coordinator: Optional[bool] = Field(
        title="Coordinador"
    )
    employee: bool = Field(
        title="empleado"
    )
    employee_email_send: bool = Field( 
        title="correo de activacion",
        default=False
    )
    season_id: int = Field( 
        title="temporada",
        default=1   
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffCatalog(BaseModel):
    id:int
    name: str
    is_active: boolean

class StaffComplete(BaseModel):
    staff: StaffModify
    vaccines : Optional[list[StaffCatalog]]
    food_restrictions : Optional[list[StaffCatalog]]