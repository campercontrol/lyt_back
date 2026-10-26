from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class CampDiscountCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del descuento",
        max_lenght= 150
    )
    amount:  condecimal(decimal_places= 2)
    date_start: datetime = Field(
        title="Inicio del descuento"
    )
    date_end: datetime = Field(
        title="Inicio del descuento"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CampDiscountModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del descuento",
        max_lenght= 150
    )
    amount:  condecimal(decimal_places= 2)
    date_start: datetime = Field(
        title="Inicio del descuento"
    )
    date_end: datetime = Field(
        title="Inicio del descuento"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

