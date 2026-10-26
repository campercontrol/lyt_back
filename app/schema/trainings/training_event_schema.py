from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class TrainingEventCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    start: datetime = Field(
        title="Inicio del campamento",
        default_factory=datetime.now
    )
    end: datetime = Field(
        title="Fin del campamento",
        default_factory=datetime.now
    )
    location: str = Field(
        title="Foto",
        max_lenght="120"
    )    
    open_enrollment: bool = Field(
        title="Registro abierto"
    ) 
    active: bool = Field(
        title="Activo"
    )
    season_id: int = Field(
        title= "Temporada id"
    )
    training_id: int = Field(
        title= "Tipo de capacitación id"
    )    
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class TrainingEventModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    start: datetime = Field(
        title="Inicio del campamento",
        default_factory=datetime.now
    )
    end: datetime = Field(
        title="Fin del campamento",
        default_factory=datetime.now
    )
    location: str = Field(
        title="Foto",
        max_lenght="120"
    )    
    open_enrollment: bool = Field(
        title="Registro abierto"
    ) 
    active: bool = Field(
        title="Activo"
    )
    season_id: int = Field(
        title= "Temporada id"
    )
    training_id: int = Field(
        title= "Tipo de capacitación id"
    )   
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )