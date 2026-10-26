from datetime import datetime, date
from typing import Optional
from uuid import UUID
from xmlrpc.client import boolean

from pydantic import BaseModel, Field, AnyUrl, condecimal

class PaymentCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    paid: bool = Field(
        title="Pagado"
    )
    payment_amount: condecimal(decimal_places= 2) # type: ignore
    
    payment_date: date = Field(
        title = "Fecha del pago",
        default_factory=datetime.now
    )
    txn_number: str = Field(
        title= "Numero de transacción",
        max_lenght= 150       
    )    
    camp_id: int = Field(
        title="Camp"
    )
    camper_id: int = Field(
        title="Camper"
    )
    currency_id: int = Field(
        title="Divisa"
    )
    parent_id: int = Field(
        title="Titular de la cuenta"
    )
    payment_method_id: int = Field(
        title="Metodo de pago"
    )
    txn_type_id: int = Field(
        title="Tipo de transacción"
    ) 
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class PaymentModify(BaseModel):
    
    paid: bool = Field(
        title="Pagado"
    )
    payment_amount: condecimal(decimal_places= 2)
    
    payment_date: date = Field(
        title = "Fecha del pago"
    )
    txn_number: str = Field(
        title= "Numero de transacción",
        max_lenght= 150       
    )    
    camp_id: int = Field(
        title="Camp"
    )
    camper_id: int = Field(
        title="Camper"
    )
    currency_id: int = Field(
        title="Divisa"
    )
    parent_id: int = Field(
        title="Titular de la cuenta"
    )
    payment_method_id: int = Field(
        title="Metodo de pago"
    )
    txn_type_id: int = Field(
        title="Tipo de transacción"
    ) 
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
class MassivePayment(BaseModel):
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    paid: Optional[bool] = Field(
        title="Pagado",
        default=False
    )
    payment_amount: condecimal(decimal_places= 2) # type: ignore
    payment_date: date = Field(
        title = "Fecha del pago",
        default_factory=datetime.now
    )
    txn_number: str = Field(
        title= "Numero de transacción",
        max_lenght= 150       
    )    
    payment_method_id: int = Field(
        title="Metodo de pago"
    )
    txn_type_id: int = Field(
        title="Tipo de transacción"
    ) 
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )
class MassivePaymentCreate(BaseModel):
    campers: list[int] = Field(
        title="lista de id´s de los campers"
    )
    payment: MassivePayment