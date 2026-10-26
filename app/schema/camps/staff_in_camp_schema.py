from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

class StaffInCampCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    confirmed_staff: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    assigned_role_id: Optional[int] = Field(
        title= "Campamento id"
    )
    camp_id: int = Field(
        title= "Campamento id"
    )
    staff_id: int = Field(
        title= "Camper id"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffInCampModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    confirmed_staff: Optional[bool] = Field(
        title="Aceptado o apuntado en el camp"
    )
    assigned_role_id: Optional[int] = Field(
        title= "Campamento id"
    )
    camp_id: int = Field(
        title= "Campamento id"
    )
    staff_id: int = Field(
        title= "Camper id"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )