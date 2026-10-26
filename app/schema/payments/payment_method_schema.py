from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class PaymentMethodCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name:str = Field(
        title= "Nombre del metodo de pago"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class PaymentMethodModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name:str = Field(
        title= "Nombre del metodo de pago"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
