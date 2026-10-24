from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field


class EmailTemplateCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    template_type: int = Field(
        title="Tipo de template"
    )

    title: str = Field(
        title="Asunto del correo"
    )

    template: str = Field(
        title="Cuerpo del correo"
    )

    order: int = Field(
        title="Orden"
    )

    created_at:datetime = Field(
        default_factory=datetime.now
    )


class EmailTemplateModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    template_type: int = Field(
        title="Tipo de template"
    )

    title: str = Field(
        title="Asunto del correo"
    )

    template: str = Field(
        title="Cuerpo del correo"
    )

    order: int = Field(
        title="Orden"
    )
    
    updated_at:datetime = Field(
        default_factory=datetime.now
    )