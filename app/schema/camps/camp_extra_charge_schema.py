from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class CampExtraChargeCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del cargo extra",
        max_lenght= 150
    )
    price:  condecimal(decimal_places= 2)
    currency_id: int = Field(
        title="Divisa"
    )
    camp_id : Optional[int] = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CampExtraChargeModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del cargo extra",
        max_lenght= 150
    )
    price:  condecimal(decimal_places= 2)
    currency_id: int = Field(
        title="Divisa"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

