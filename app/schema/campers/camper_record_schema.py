from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class CamperRecordCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    attend: int = Field(
        title="Proximos campamentos"
    )
    attended: int = Field(
        title="Campamentos pasados"
    )
    total: int = Field(
        title="Campamentos en total"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CamperRecordModify(BaseModel):
       
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    attend: int = Field(
        title="Proximos campamentos"
    )
    attended: int = Field(
        title="Campamentos pasados"
    )
    total: int = Field(
        title="Campamentos en total"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

