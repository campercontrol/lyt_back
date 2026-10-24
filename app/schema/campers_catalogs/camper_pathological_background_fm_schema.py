from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

class CamperPathologicalBackFmCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    camper_id:int = Field(
        title='Camper id',
    )
    pathological_background_fm_id:int = Field(
        title='Pathological Background Family id',
    )
    is_active: bool = Field(
        title='ACtivo en el camper'
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class CamperPathologicalBackFmModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    camper_id:int = Field(
        title='Camper id',
    )
    pathological_background_family_id:int = Field(
        title='Pathological Background Family id',
    )
    is_active: bool = Field(
        title='ACtivo en el camper'
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )