from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

class StaffInTrainingCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    assist: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    confirmed_staff: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    training_event_id: int = Field(
        title= "Evento de capacitación id"
    )
    staff_id: int = Field(
        title= "Staff id"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffInTrainingModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    assist: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    confirmed_staff: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    training_event_id: int = Field(
        title= "Evento de capacitación id"
    )
    staff_id: int = Field(
        title= "Staff id"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )