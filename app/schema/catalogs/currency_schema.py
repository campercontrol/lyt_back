from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title='Nombre de la divisa',
        max_length=150,
    )
    symbol:str= Field(
        title='Simbolo de la divisa',
        max_lenght=10,
    )
    acronyms:str= Field(
        title='Siglas',
        max_lenght= 10,
    )
    created_at:datetime = Field(
        default_factory=datetime.now
    )


class CurrencyModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name:str = Field(
        title='Nombre de la divisa',
        max_length=150,
    )
    symbol:str= Field(
        title='Simbolo de la divisa',
        max_lenght=10,
    )

    acronyms:str= Field(
        title='Siglas',
        max_lenght= 10,
    )
    updated_at:datetime = Field(
        default_factory=datetime.now
    )