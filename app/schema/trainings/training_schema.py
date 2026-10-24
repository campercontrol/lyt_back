from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class TrainingCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del tipo de capacitación",
        max_lenght= 150
    )
    photo: str = Field(
        title="Foto"
    )
    description: str = Field(
        title="Descripción."
    )
    url: AnyUrl = Field(
        title="Pagina web para mas información",
        max_lenght= 150
    )    
    active: bool = Field(
        title="Activo"
    )    
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class TrainingModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del tipo de capacitación",
        max_lenght= 150
    )
    photo: str = Field(
        title="Foto"
    )
    description: str = Field(
        title="Descripción."
    )
    url: AnyUrl = Field(
        title="Pagina web para mas información",
        max_lenght= 150
    )    
    active: bool = Field(
        title="Activo"
    )    
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )