from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal


class StaffRoleCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title='Nombre del rol',
        max_length=150,
    )
    payment:float = Field(
        title='Pago por día'
    )
    color:str = Field(
        title='color de etiqueta',
        max_lenght=15,
    )
    created_at:datetime = Field(
        default_factory=datetime.now
    )


class StaffRoleModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title='Nombre del rol',
        max_length=150,
    )
    payment:float = Field(
        title='Pago por día'
    )
    color:str = Field(
        title='color de etiqueta',
        max_lenght=15,
    )
    updated_at:datetime = Field(
        default_factory=datetime.now
    )