from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

class SeasonCreate(BaseModel):
    
    id:Optional[int] = Field(
        title = "id",
        default = None, 
        primary_key = True
    )

    name:str = Field(
        title= "Nombre de la temporada",
        max_lenght= 150
    )
    current:bool = Field(
        title="Temporada actual"
    )
    created_at:datetime = Field(
        default_factory=datetime.now
    )

class SeasonModify(BaseModel):
    
    id:Optional[int] = Field(
        title = "id",
        default = None, 
        primary_key = True
    )

    name:str = Field(
        title= "Nombre de la temporada",
        max_lenght= 150
    )
    current:bool = Field(
        title="Temporada actual"
    )
    updated_at:datetime = Field(
        default_factory=datetime.now
    )
