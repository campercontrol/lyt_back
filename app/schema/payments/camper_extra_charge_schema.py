from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class CamperExtraChargeCreate(BaseModel):
   
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    is_selected:bool = Field(
        title= "Nombre del metodo de pago"
    )
    camper_id:int = Field(
        title="Camper"
    )
    extra_charge_id:int = Field(
        title="Cargo Extra"
    )
    created_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )


class CamperExtraChargeModify(BaseModel):
    
    id:Optional[int] = Field(
        title="Id",
        default=None,
        primary_key=True
    ) 
    is_selected:bool = Field(
        title= "Nombre del metodo de pago"
    )
    camper_id:int = Field(
        title="Camper"
    )
    extra_charge_id:int = Field(
        title="Cargo Extra"
    )
    updated_at:Optional[datetime] = Field(
        default_factory=datetime.now
    )

class UpdateCamperExtraCharge(BaseModel):
    id: int = Field(
        title="ID del cargo extra del camper",
    )
    is_selected:bool = Field(
        title= "Nombre del metodo de pago"
    )

class ExtraChargeListCreate(BaseModel):
    extra_charge_id:int = Field(
        title="Cargo Extra Id"
    )
    extra_charge_name: str = Field(
        title="Nombre del cargo extra"
    )
    extra_charge_price: int = Field(
        title= "Precio del cargo extra"
    )
    extra_selected:bool = Field(
        title= "Nombre del metodo de pago"
    )
    camper_id:int = Field(
        title="Camper"
    )
    

class CamperExtraChargeListCreate(BaseModel):
    extra_charges: list[ExtraChargeListCreate]

class ExtraChargeMultiple(BaseModel):
    
    camp_id: int = Field(
        title= "ID del camp"
    )
    camp_extra_charge_is_selected:bool = Field(
        title="Seleccionado"
    )
    camp_extra_charge_id:int = Field(
        title = "Cargo extra id"
    )
    camp_extra_charge_name: str = Field(
        title = "Nombre del cargo extra"
    )
    camp_extra_charge_price: str = Field(
        title = "precio del cargo extra"
    )
    camper_extra_charge_id: int = Field(
        title = "Id del cargo del camper"
    )
    # camper_extra_charge_payment_id: int = Field(
    #     title = "ID del payment asociado al cargo extra del camper"
    # )
    # extra_charge_symbol: str = Field(
    #     title = "Nombre del cargo extra"
    # )
    # extra_selected: boolean = Field(
    #     title = "Cargo seleccionado"
    # )
    # camper_id: int = Field(
    #     title = "ID del camper"
    # )
