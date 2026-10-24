from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

class DoctorCreate(BaseModel):
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
    cellphone:str = Field(
        title="Celular"
    )   
    login_id:int = Field(
        title="Usuario"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class DoctorModify(BaseModel):
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
    cellphone:str = Field(
        title="Celular"
    )   
    login_id:int = Field(
        title="Usuario"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
