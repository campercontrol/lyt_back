from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

class StaffCommentCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    comment: str = Field(
        title="Status de inscripción"
    )

    is_public: bool = Field(
        title="Comentario publico"
    )
    show_to: int= Field(
        title="A quien se muestra el comentario"
    )
    user_id: int = Field(
        title= "Usuario que creo el comentario"
    )
    staff_id: int = Field(
        title= "Staff id"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffCommentModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    comment: str = Field(
        title="Status de inscripción"
    )

    is_public: bool = Field(
        title="Comentario publico"
    )
    show_to: int= Field(
        title="A quien se muestra el comentario"
    )
    user_id: int = Field(
        title= "Usuario que creo el comentario"
    )
    staff_id: int = Field(
        title= "Staff id"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )