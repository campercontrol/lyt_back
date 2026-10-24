from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from schema.user import UserCreate

from pydantic import BaseModel, Field

class ParentCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True,
        gt=0
    ) 
    user_id:Optional[int]
    tutor_name:str = Field(
        title="Nombre",
        max_lenght= 512
    ) 
    tutor_lastname_father:str = Field(
        title="Primer Apellido",
        max_lenght= 512
    ) 
    tutor_lastname_mother: Optional[str] = Field(
        title="Segundo Apellido",
        max_lenght= 512
    ) 
    tutor_cellphone:str = Field(
        title="Celular",
        mas_lenght=30
    ) 
    tutor_home_phone: Optional[str] = Field(
        title="Telefono de casa",
        mas_lenght=30
    ) 
    tutor_work_phone: Optional[str] = Field(
        title="Telefono de trabajo",
        mas_lenght=30
    ) 
    contact_name:str = Field(
        title="Nombre del segundo tutor",
        max_lenght=512
    ) 
    contact_lastname_father:str = Field(
        title="Primer apellido del segundo tutor",
        max_lenght=512
    ) 
    contact_lastname_mother: Optional[str] = Field(
        title="Segundo apellido del segundo tutor",
        max_lenght=512
    ) 
    contact_cellphone:str = Field(
        title="Celular del segundo tutor",
        max_lenght=30
    ) 
    contact_home_phone: Optional[str] = Field(
        title="Telefono de casa del segundo tutor",
        max_lenght=30
    ) 
    contact_work_phone: Optional[str] = Field(
        title="Telefono de trabajo del segundo tutor",
        max_lenght=30
    ) 
    contact_email:str = Field(
        title="Email del segundo tutor",
        max_lenght=75
    ) 
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class ParentModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True,
        gt=0
    ) 
    tutor_name:str = Field(
        title="Nombre",
        max_lenght= 512
    ) 
    tutor_lastname_father:str = Field(
        title="Primer Apellido",
        max_lenght= 512
    ) 
    tutor_lastname_mother: Optional[str] = Field(
        title="Segundo Apellido",
        max_lenght= 512
    ) 
    tutor_cellphone:str = Field(
        title="Celular",
        mas_lenght=30
    ) 
    tutor_home_phone: Optional[str] = Field(
        title="Telefono de casa",
        mas_lenght=30
    ) 
    tutor_work_phone: Optional[str] = Field(
        title="Telefono de trabajo",
        mas_lenght=30
    ) 
    contact_name:str = Field(
        title="Nombre del segundo tutor",
        max_lenght=512
    ) 
    contact_lastname_father:str = Field(
        title="Primer apellido del segundo tutor",
        max_lenght=512
    ) 
    contact_lastname_mother: Optional[str] = Field(
        title="Segundo apellido del segundo tutor",
        max_lenght=512
    ) 
    contact_cellphone:str = Field(
        title="Celular del segundo tutor",
        max_lenght=30
    ) 
    contact_home_phone: Optional[str] = Field(
        title="Telefono de casa del segundo tutor",
        max_lenght=30
    ) 
    contact_work_phone: Optional[str] = Field(
        title="Telefono de trabajo del segundo tutor",
        max_lenght=30
    ) 
    contact_email:str = Field(
        title="Email del segundo tutor",
        max_lenght=75
    )  
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class ParentCompleteCreate(BaseModel):
    
    user: UserCreate
    parent: ParentCreate


## Falta agregar max_lenght