from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class CampCheckpointCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del cargo extra",
        max_lenght= 150
    )
    chekpoint_date: date = Field(
        title= "Fecha del checkpoint"
    )
    order: int = Field(
        title= "orden de checkpoints"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CampCheckpointModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del cargo extra",
        max_lenght= 150
    )
    chekpoint_date: date = Field(
        title= "Fecha del checkpoint"
    )
    order: int = Field(
        title= "orden de checkpoints"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

