from datetime import date, datetime, datetime
from typing import Optional, List
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 

    name: str = Field(
        title="Nombre de la campaña"
    ) 

    camp_parents: Optional[boolean]  = Field(
        title="Mandar a titulares de la cuenta"
    )

    camp_staff: Optional[boolean]  = Field(
        title="Mandar a staff"
    )

    camp_school:Optional[boolean]  = Field(
        title="Mandar a el colegio"
    )

    active_time: Optional[str] = Field(
        title="Tiempo para enviar",
        default="1"
    )

    send: boolean  = Field(
        title="Mandar a el colegio"
    )

    camp_id: Optional[int] = Field(
        title="Tipo de template"
    )

    season_id: Optional[int] = Field(
        title="Temporada"
    )

    send_type_id: int = Field(
        title="Tipo de envío"
    )

    training_event_id: Optional[int] = Field(
        title="Capacitación"
    )

    template_id: int = Field(
        title="Template"
    )

    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CampaignModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
     
    name: str = Field(
        title="Nombre de la campaña"
    ) 

    camp_parents: Optional[boolean]  = Field(
        title="Mandar a titulares de la cuenta"
    )

    camp_staff: Optional[boolean]  = Field(
        title="Mandar a staff"
    )

    camp_school:Optional[boolean]  = Field(
        title="Mandar a el colegio"
    )

    active_time: Optional[str] = Field(
        title="Tiempo para enviar",
        default="1"
    )

    send: boolean  = Field(
        title="Mandar a el colegio"
    )

    camp_id: Optional[int] = Field(
        title="Tipo de template"
    )

    season_id: Optional[int] = Field(
        title="Temporada"
    )

    send_type_id: int = Field(
        title="Tipo de envío"
    )

    training_event_id: Optional[int] = Field(
        title="Capacitación"
    )

    template_id: int = Field(
        title="Template"
    )

    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now
    )

class MailingTypeSelect(BaseModel):

    camps_id:List[int] = Field(
        title = "campamentos"
    )
    staffs: bool = Field(
        title= "Se envia a staff"
    )
    campers: bool = Field(
        title= "Se envia a campers"
    )
    schools: bool = Field(
        title= "Se envia a escuelas"
    )
    training_id: int = Field(
        title = "Capacitación"
    )
    season: int = Field(
        title = "Temporada"
    )


class CampaignSend(BaseModel):

    campaign : CampaignCreate = Field(
        title = "Campaña"
    )
    camps: "list[dict]" = Field(
        title = "Datos del camp"
    )
    template_body: str = Field(
        title = "Cuerpo del correo"
    )
    email_subject: str = Field(
        title= "Asunto del correo"
    )
class CampaignSendStaff(BaseModel):
    campaign : CampaignCreate = Field(
        title = "Campaña"
    )
    staffs: "list[dict]" = Field(
        title = "Datos del camp"
    )
    template_title: str = Field(
        title = "Asunto del correo"
    )
    email_subject: Optional[str] = Field(
        title= "Asunto del correo"
    )


class CamperCampaignCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    campaign_id: int = Field(
        title = "Campaña"
    )
    camp_id: int =  Field(
        title = "Camp"
    )
    camper_id: int  =  Field(
        title = "Camper"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffCampaignCreate(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    campaign_id: int = Field(
        title = "Campaña"
    )
    camp_id: Optional[int] =  Field(
        title = "Camp"
    )
    staff_id: int  =  Field(
        title = "Camper"
    )
    training_event_id: Optional[int] =  Field(
        title = "Training Event"
    )
    season_id: Optional[int] =  Field(
        title =  "Temporada"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class SchoolCampignCreate(BaseModel):

    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    campaign_id: int = Field(
        title =  "Campaña"
    )
    camp_id: int =  Field(
        title = "Campamento"
    )
    school_id: int =  Field(
        title = "Escuela"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
