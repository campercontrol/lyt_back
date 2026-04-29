from datetime import datetime
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, condecimal

from schema.camps.camp_extra_charge_schema import CampExtraChargeCreate
from schema.camps.camp_extra_question_schema import CampExtraQuestionCreate



class CampCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del campamento",
        max_lenght= 150
    )
    start: datetime = Field(
        title="Inicio del campamento",
        default=datetime.now()
    )
    end: datetime = Field(
        title="Fin del campamento",
        default=datetime.now()
    )
    start_registration: datetime = Field(
        title="Inicio de registro",
        default=datetime.now()
    )
    end_registration: datetime = Field(
        title="Fin de registro",
        default=datetime.now()
    )
    registration: bool = Field(
        title="Registro abierto"
    )
    url: Optional[str] = Field(
        title="Pagina web para mas información",
        max_lenght= 150,
        default=None
    )
    special_message: str = Field(
        title="Mensaje para titulares de la cuenta."
    )
    special_message_admin: str = Field(
        title="Mensaje especial solo visible para administradores"
    )
    public_price: condecimal(decimal_places= 2)

    show_payment_parent: bool = Field(
        title="Mostrar pago a titulares de la cuenta"
    )
    show_rebate_parent: bool = Field(
        title="Mostrar descuento a titulares de la cuenta"
    )
    show_paypal_button: bool = Field(
        title="Activar boton de paypal para este campamento"
    )
    show_payment_order: bool = Field(
        title="Mostrar orden de pago a titulares de la cuenta"
    )
    show_mercadopago_button: bool = Field(
        title="Mostrar botón de mercado pago para este campamento",
        default=False
    )
    recommended_payment_dates: str = Field(
        title="Fechas recomendadas de pago para este campamento"
    )
    reminder_camp_days: int = Field(
        title="Dias antes para recordar del campamento"
    )
    reminder_discount_days: int = Field(
        title="Dias antes para recordar del descuento"
    )
    insurance: condecimal(decimal_places= 2)

    venue: str = Field(
        title="Punto de reunión",
        max_lenght= 150
    )
    photo_url: Optional[str] = Field(
        title="Url para la galeria de fotos",
        default=None
    )
    photo_password: Optional[str] = Field(
        title="Contraseña para galeria de fotos",
        default="Por confirmar"
    )
    medical_report: str = Field(
        title="Reporte medico"
    )
    occupancy_camp: int = Field(
        title="Capacidad maxima del campamento"
    )
    active: bool = Field(
        title="Campamento activo"
    )
    general_camp: bool = Field(
        title="Campamento de verano"
    )
    currency_id: int = Field(
        title="Divisa dentro de campamento"
    )
    location_id: Optional[int] = Field(
        title="Sede del campamento"
    )
    school_id: int = Field(
        title="Escuela del campamento"
    )
    season_id: int = Field(
        title="Temporada del campamento"
    )
    
    created_at:Optional[datetime] = Field(
        default=datetime.now()
    )


class CampModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name: str = Field(
        title="Nombre del campamento",
        max_lenght= 150
    )
    start: datetime = Field(
        title="Inicio del campamento",
        default=datetime.now()
    )
    end: datetime = Field(
        title="Fin del campamento",
        default=datetime.now()
    )
    start_registration: datetime = Field(
        title="Inicio de registro",
        default=datetime.now()
    )
    end_registration: datetime = Field(
        title="Fin de registro",
        default=datetime.now()
    )
    registration: bool = Field(
        title="Registro abierto"
    )
    url: str = Field(
        title="Pagina web para mas información",
        max_lenght= 150
    )
    special_message: str = Field(
        title="Mensaje para titulares de la cuenta."
    )
    special_message_admin: str = Field(
        title="Mensaje especial solo visible para administradores"
    )
    public_price: condecimal(decimal_places= 2)
    
    show_payment_parent: bool = Field(
        title="Mostrar pago a titulares de la cuenta"
    )
    show_rebate_parent: bool = Field(
        title="Mostrar descuento a titulares de la cuenta"
    )
    show_paypal_button: bool = Field(
        title="Activar boton de paypal para este campamento"
    )
    show_payment_order: bool = Field(
        title="Mostrar orden de pago a titulares de la cuenta"
    )
    reminder_camp_days: int = Field(
        title="Dias antes para recordar del campamento"
    )
    reminder_discount_days: int = Field(
        title="Dias antes para recordar del descuento"
    )
    insurance:  condecimal(decimal_places= 2)
    
    venue: str = Field(
        title="Punto de reunión",
        max_lenght= 150
    )
    photo_url: str = Field(
        title="Url para la galeria de fotos"
    )
    photo_password: str = Field(
        title="Contraseña para galeria de fotos"
    )
    medical_report: str = Field(
        title="Reporte medico"
    )
    occupancy_camp: int = Field(
        title="Capacidad maxima del campamento"
    )
    active: bool = Field(
        title="Campamento activo"
    )
    general_camp: bool = Field(
        title="Campamento de verano"
    )
    currency_id: int = Field(
        title="Divisa dentro de campamento"
    )
    location_id: Optional[int] = Field(
        title="Sede del campamento"
    )
    school_id: int = Field(
        title="Escuela del campamento"
    )
    season_id: int = Field(
        title="Temporada del campamento"
    )
    updated_at:Optional[datetime] = Field(
        default=datetime.now()
    )
class MailingCamps(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

    
class PaymentAccount(BaseModel):
    id:int
class CampDiscountCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    name : str = Field(
        title = "Nombre del descunto"
    )
    amount: condecimal(decimal_places= 2)
    
    camp_id:Optional[int] = Field(
        title = "Id del campamento"
    )
    date_start:Optional[datetime] = Field(
        default=datetime.now()
    )
    date_end:Optional[datetime] = Field(
        default=datetime.now()
    )


class CampPaymentAccountCreate(BaseModel):
    camp : CampCreate
    payment_accounts: Optional[list[PaymentAccount]]


class CampComplete(BaseModel):
    camp: CampCreate
    payment_accounts: Optional[list[PaymentAccount]]
    extra_charges: Optional[list[CampExtraChargeCreate]]
    extra_question: Optional[list[CampExtraQuestionCreate]]
    extra_discounts: Optional[list[CampDiscountCreate]]

class CampSearch(BaseModel):
    name: Optional[str] = Field(
        title="Nombre del campamento",
        default=''
    )
    location: Optional[str] = Field(
        title="Sede",
        default=''
    )
    school: Optional[str] = Field(
        title="School",
        default=''
    )