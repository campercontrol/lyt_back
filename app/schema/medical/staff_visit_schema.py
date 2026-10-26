from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

class StaffVisitCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    medical_tracing:bool = Field(
        title="Consulta de seguimiento"
    ) 
    doctor:str = Field(
        title="Nombre del doctor"
    )
    attention_date:date = Field(
        title="Fecha de la cita medica"
    )
    attention_time:time = Field(
        title="Hora de la cita medica"
    )    
    diagnostic:str = Field(
        title="Diagnostico"
    )  
    description:str = Field(
        title="Descripción basica para personal no medico"
    )
    triage:int = Field(
        title="Nivel de triage"
    )
    camp_restriction:str = Field(
        title="Restricciones o medidas dentro del campamento"
    )
    administered_medications:str = Field(
        title="Tratamiento"
    )
    medical_monitoring:str = Field(
        title="Recomendaciones para seguimiento posterior al campamento" 
    )
    comment:str = Field(
        title="Comentario de la consulta"
    )
    camp_id:int = Field(
        title="Campamento"
    )
    staff_id:int = Field(
        title="Staff"
    )
    initial_visit_id:int = Field(
        title="Consulta medica principal"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class StaffVisitModify(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )      
    medical_tracing:bool = Field(
        title="Consulta de seguimiento"
    ) 
    doctor:str = Field(
        title="Nombre del doctor"
    )
    attention_date:date = Field(
        title="Fecha de la cita medica"
    )
    attention_time:time = Field(
        title="Hora de la cita medica"
    )    
    diagnostic:str = Field(
        title="Diagnostico"
    )  
    description:str = Field(
        title="Descripción basica para personal no medico"
    )
    triage:int = Field(
        title="Nivel de triage"
    )
    medication_authorization:str = Field(
        title="¿Quien autorizó el medicamento"
    )
    event_description:str = Field(
        title="Descripción del evento en palabras del camper"
    )
    camp_restriction:str = Field(
        title="Restricciones o medidas dentro del campamento"
    )
    administered_medications:str = Field(
        title="Tratamiento"
    )
    medical_monitoring:str = Field(
        title="Recomendaciones para seguimiento posterior al campamento" 
    )
    comment:str = Field(
        title="Comentario de la consulta"
    )
    medical_comment:str = Field(
        title="Comentario solo para medicos y staff"
    )
    send_in_email:bool = Field(
        title="Enviar consulta a padres" 
    )
    already_sent:bool = Field(
        title="Consulta enviada" 
    )
    camp_id:int = Field(
        title="Campamento"
    )
    camper_id:int = Field(
        title="Camper"
    )
    initial_visit_id:int = Field(
        title="Consulta medica principal"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
