from datetime import date, datetime, datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

class TrophyCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title= "Nombre del trofeo"
    )
    description: str = Field(
        title= "Nombre del trofeo"
    )
    photo: str =  Field(
        title= "Fotografia del trofeo" 
    )
    active: boolean = Field(
        title = "Trofeo activo"
    )
    trophy_type: int = Field(
        title = "Tipo de trofeo"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class TrophyModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title= "Nombre del trofeo"
    )
    description: str = Field(
        title= "Nombre del trofeo"
    )
    photo: str =  Field(
        title= "Fotografia del trofeo" 
    )
    active: boolean = Field(
        title = "Trofeo activo"
    )
    trophy_type: int = Field(
        title = "Tipo de trofeo"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class TrophySeasonCreate(BaseModel):
    id: Optional[int] = Field(
        title = "Id",
        default =  None,
        primary_key = True
    )
    season_id: int =  Field(
        title= "Temporada"
    )
    trophy_id: int = Field(
        title= "Trofeo para ser asignado"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    


class TrophySeasonModify(BaseModel):
    id: Optional[int] = Field(
        title = "Id",
        default =  None,
        primary_key = True
    )
    season_id: int =  Field(
        title= "Temporada"
    )
    trophy_id: int = Field(
        title= "Trofeo para ser asignado"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    

class TrophyStaffCreate(BaseModel):
    id: Optional[int] = Field(
        title = "Id",
        default =  None,
        primary_key = True
    )
    trophy_season_id: int = Field(
        title="Relacion de trofeo con temporada"
    )
    staff_id : int = Field(
        title="Staff"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class TrophyStaffModify(BaseModel):
    id: Optional[int] = Field(
        title = "Id",
        default =  None,
        primary_key = True
    )
    trophy_season_id: int = Field(
        title="Relacion de trofeo con temporada"
    )
    staff_id : int = Field(
        title="Staff"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )