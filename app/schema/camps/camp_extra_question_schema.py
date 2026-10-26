from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl

class CampExtraQuestionCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    question: str = Field(
        title="Pregunta",
        max_lenght= 150
    )
    is_required: bool = Field(
        title="Obligatoria"
    )
    camp_id : Optional[int] = Field(
        title="Campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CampExtraQuestionModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    question: str = Field(
        title="Pregunta",
        max_lenght= 150
    )
    is_required: bool = Field(
        title="Obligatoria"
    )
    camp_id : int = Field(
        title="Campamento"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

