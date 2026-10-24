from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from xmlrpc.client import boolean

from schema.catalogs.vaccine_schema import VaccineCreate

from pydantic import BaseModel, Field

class CamperExtraAnswerCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    answer:str = Field(
        title="Respuesta"
    )
    camper_id:int = Field(
        title="Camper"
    )
    question_id:int = Field(
        title="Pregunta extra"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
class UpdateCamperExtraAnswer(BaseModel):
    id: int = Field(
        title="ID de la respuesta del camper de la pregunta extra"
    ) 
    answer:str = Field(
        title="Respuesta del camper a la pregunta extra"
    )

class CamperExtraAnswerModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    answer:str = Field(
        title="Respuesta"
    )
    camper_id:int = Field(
        title="Camper"
    )
    question_id:int = Field(
        title="Pregunta extra"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class ExtraAnswerListCreate(BaseModel):
  
    id:str = Field(
        title="Respuesta"
    )
    question: str = Field(
        title="Pregunta"
    )
    is_required: bool = Field(
        title="Pregunta obligatoria"
    )
    camper_id: int = Field(
        title= "Id del camper"
    )
    answer: str = Field(
        title="Respuesta del camper"
    )

class CamperExtraAnswerListCreate(BaseModel):
    extra_answers: List[ExtraAnswerListCreate]


class ExtraAnswerMultiple(BaseModel):
    
    answer:str = Field(
        title="Respuesta"
    )
    camper_extra_answer_id:int = Field(
        title = "ID de la respuesta del camper"
    )
    question_id:int = Field(
        title = "Pregunta"
    )
    