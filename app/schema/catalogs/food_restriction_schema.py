from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field


class FoodRestrictionCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title='Nombre de la restricción de comida',
        max_length=150,
    )
    assigned_id:int
    order:int
    created_at:datetime = Field(
        default_factory=datetime.now
    )



class FoodRestrictionModify(BaseModel):
   
    name:str = Field(
        title='Nombre de la restricción de comida',
        max_length=150,
    )
    assigned_id:int
    order:int
    updated_at:datetime = Field(
        default_factory=datetime.now
    )