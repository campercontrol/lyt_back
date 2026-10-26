from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

class LocationCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre de la sede",
        max_lenght=150
    )
    phone: str = Field(
        title="Telefono",
        max_lenght=30
    )
    email: str = Field(
        title="Correo de contacto",
        max_lenght=50
    )
    contact: str = Field(
        title="Nombre la persona de contacto",
        max_lenght=150
    )
    address: str = Field(
        title="Dirección",
        max_lenght=512
    )
    url: str = Field(
        title="Pagina web",
        max_lenght=150
    )
    active: bool = Field(
        title="Activa"
    )
    created_at:datetime = Field(
        default_factory=datetime.now
    )

class LocationModify(BaseModel):
    name: str = Field(
        title="Nombre de la sede",
        max_lenght=150
    )
    phone: str = Field(
        title="Telefono",
        max_lenght=30
    )
    email: str = Field(
        title="Correo de contacto",
        max_lenght=50
    )
    contact: str = Field(
        title="Nombre la persona de contacto",
        max_lenght=150
    )
    address: str = Field(
        title="Dirección",
        max_lenght=512
    )
    url: str = Field(
        title="Pagina web",
        max_lenght=150
    )
    active: bool = Field(
        title="Activa"
    )
    updated_at:datetime = Field(
        default_factory=datetime.now
    )