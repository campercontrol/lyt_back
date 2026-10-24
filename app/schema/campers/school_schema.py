from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

class SchoolCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    login_email: str = Field(
        title= "Correo"
    )
    password: str = Field(
        title="contraseña"
    )
    name:str  = Field(
        title="Nombre",
        max_lenght= 100
    ) 
    address: Optional[str]  = Field(
        title="Dirección"
    ) 
    url: Optional[str]  = Field(
        title="Pagina web",
        max_lenght= 100
    ) 
    contact: Optional[str]  = Field(
        title="Persona de contacto",
        max_lenght= 50
    ) 
    phone: Optional[str]  = Field(
        title="Telefono de primer contacto",
        max_lenght= 15
    ) 
    cellphone: Optional[str]  = Field(
        title="Celular de primer contacto",
        max_lenght= 15
    ) 
    contact_first_email: Optional[str]  = Field(
        title="Email de primer contacto",
        max_lenght= 30
    ) 
    contact_second_name: Optional[str]  = Field(
        title="Segundo contacto",
        max_lenght= 50
    ) 
    contact_second_phone: Optional[str]  = Field(
        title="Telefono segundo contacto",
        max_lenght= 15
    ) 
    contact_second_cellphone: Optional[str]  = Field(
        title="Celular segundo contacto",
        max_lenght= 15
    ) 
    contact_second_email: Optional[str]  = Field(
        title="Email segundo contacto",
        max_lenght= 30
    ) 
    contact_third_name: Optional[str]  = Field(
        title="Tercer contacto",
        max_lenght= 50
    ) 
    contact_third_phone: Optional[str]  = Field(
        title="Telefono tercer contacto",
        max_lenght= 15
    ) 
    contact_third_cellphone: Optional[str]  = Field(
        title="Celular tercer contacto",
        max_lenght= 15
    ) 
    contact_third_email: Optional[str]  = Field(
        title="Email tercer contacto",
        max_lenght= 30
    ) 
    verify:boolean  = Field(
        title="Permitir acceso a la plataforma"
    ) 
    active:boolean  = Field(
        title="Activa"
    ) 
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class SchoolModify(BaseModel):
    
    login_id:Optional[int] = Field(
        title= "Usuario"
    )  
    name:str  = Field(
        title="Nombre",
        max_lenght= 100
    ) 
    address: Optional[str]  = Field(
        title="Dirección"
    ) 
    url: Optional[str]  = Field(
        title="Pagina web",
        max_lenght= 100
    ) 
    contact: Optional[str]  = Field(
        title="Persona de contacto",
        max_lenght= 50
    ) 
    phone: Optional[str]  = Field(
        title="Telefono de primer contacto",
        max_lenght= 15
    ) 
    cellphone: Optional[str]  = Field(
        title="Celular de primer contacto",
        max_lenght= 15
    ) 
    email: Optional[str]  = Field(
        title="Email de contacto",
        max_lenght= 30
    ) 
    contact_second_name: Optional[str]  = Field(
        title="Segundo contacto",
        max_lenght= 50
    ) 
    contact_second_phone: Optional[str]  = Field(
        title="Telefono segundo contacto",
        max_lenght= 15
    ) 
    contact_second_cellphone: Optional[str]  = Field(
        title="Celular segundo contacto",
        max_lenght= 15
    ) 
    contact_second_email: Optional[str]  = Field(
        title="Email segundo contacto",
        max_lenght= 30
    ) 
    contact_third_name: Optional[str]  = Field(
        title="Tercer contacto",
        max_lenght= 50
    ) 
    contact_third_phone: Optional[str]  = Field(
        title="Telefono tercer contacto",
        max_lenght= 15
    ) 
    contact_third_cellphone: Optional[str]  = Field(
        title="Celular tercer contacto",
        max_lenght= 15
    ) 
    contact_third_email: Optional[str]  = Field(
        title="Email tercer contacto",
        max_lenght= 30
    ) 
    verify:boolean  = Field(
        title="Permitir acceso a la plataforma"
    ) 
    active:boolean  = Field(
        title="Activa"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class UpdateSchool(BaseModel):
    school: SchoolModify
    password: str = Field (
        title="password"
    )
    email: str = Field (
        title = "login_email"
    )
