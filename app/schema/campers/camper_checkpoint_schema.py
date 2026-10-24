from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class CamperCheckpointCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    checkin: bool = Field(
        title="Nombre del cargo extra",
    )
    checkin_date: datetime = Field(
        title= "Fecha del checkpoint"
    )
    checkpoint_id: int = Field(
        title="Campamento"
    )
    camper_id: int = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CamperCheckpointModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    checkin: bool = Field(
        title="Nombre del cargo extra",
    )
    checkin_date: datetime = Field(
        title= "Fecha del checkpoint"
    )
    checkpoint_id: int = Field(
        title="Campamento"
    )
    camper_id: int = Field(
        title="Campamento"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

