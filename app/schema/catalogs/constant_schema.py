from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field


class ConstantCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    value:str = Field(
        title='Valor a mostrar',
        max_length=512,
    )
    num_id:int= Field(
        title='Numero de la constante',
    )
    language:str= Field(
        title='Idioma de la constante',
        max_lenght= 2,
    )
    model_name:str= Field(
        title='Tipo de constante'        
    )
    created_at:datetime = Field(
        default_factory=datetime.now
    )



class ConstantModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    value:str = Field(
        title='Valor a mostrar',
        max_length=512,
    )
    num_id:int= Field(
        title='Numero de la constante',
    )
    language:str= Field(
        title='Idioma de la constante',
        max_lenght= 2,
    )
    model_name:str= Field(
        title='Tipo de constante'        
    )
    updated_at:datetime = Field(
        default_factory=datetime.now
    )