from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

class CamperInCampCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    status: int = Field(
        title="Status de inscripción"
    )

    payment_balance : condecimal(decimal_places = 2)

    camp_id: int = Field(
        title= "Campamento id"
    )
    camper_id: int = Field(
        title= "Camper id"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class CamperInCampModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    status: int = Field(
        title="Status de inscripción"
    )
    payment_balance : condecimal(decimal_places = 2)

    camp_id: int = Field(
        title= "Campamento id"
    )
    camper_id: int = Field(
        title= "Camper id"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )