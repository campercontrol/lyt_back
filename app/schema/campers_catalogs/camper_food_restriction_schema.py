from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

class CamperFoodRestrictionCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    camper_id:int = Field(
        title='Camper id',
    )
    food_restriction_id:int = Field(
        title='Food restriction id',
    )
    is_active: bool = Field(
        title='ACtivo en el camper'
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class CamperFoodRestrictionModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    camper_id:int = Field(
        title='Camper id',
    )
    food_restriction_id:int = Field(
        title='Food restriction id',
    )
    is_active: bool = Field(
        title='ACtivo en el camper'
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )