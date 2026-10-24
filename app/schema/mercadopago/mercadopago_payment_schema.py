from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class MercadopagoPaymentCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    payment_id:int = Field(
        title="id del pago de mercadopago"
    )
    status:str = Field(
        title="Estatus del pago"
    )
    external_id:str = Field(
        title="id externo de mercadopago (ID interno generado en campercontrol)"
    )
    internal_payment_id:Optional[int] = Field(
        default=None
    )
    camper_id:int = Field(
        title="Id del camper"
    )
    camp_id:int = Field(
        title="Id del campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    
class MercadopagoPaymentUpdate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    payment_id:int = Field(
        title="id del pago de mercadopago"
    )
    status:str = Field(
        title="Estatus del pago"
    )
    external_id:str = Field(
        title="id externo de mercadopago (ID interno generado en campercontrol)"
    )
    internal_payment_id:Optional[int] = Field(
        default=None
    )
    camper_id:int = Field(
        title="Id del camper"
    )
    camp_id:int = Field(
        title="Id del campamento"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )