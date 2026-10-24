from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class MercadopagoMerchantOrderCreate(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    )
    merchant_order_id:int = Field(
        title="id del pago de mercadopago"
    )
    external_id:str = Field(
        title="id externo de mercadopago (ID interno generado en campercontrol)"
    )
    status:str = Field(
        title="Estatus de la merchant order"
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