import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, SmallInteger, Float, Text, Date
from sqlalchemy.dialects.postgresql import UUID

from utils.db import Base

class School(Base):
    __tablename__ = 'campers_school'

    uid = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        index=True,
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, doc="id de la escuela")
    login_id = Column(ForeignKey("user.id"), doc='Usuario')
    name = Column(String(512), nullable=False, doc="Nombre de la escuela")
    address = Column(Text, doc="Dirección de la escuela")
    url = Column(String(512,), doc="Pagina web de la escuela")
    contact = Column(String(512), doc="Persona de contacto en la escuela")
    phone = Column(String(100), doc="Telefono de la escuela")
    cellphone = Column(String(100), doc="Celular del contacto en la escuela")
    email = Column(String(512), doc="Email de contacto de la escuela")
    contact_second_name = Column(String(512), doc="Email de un segundo contacto de la escuela")
    contact_second_phone = Column(String(100), doc="Segundo telefono de la escuela")
    contact_second_cellphone = Column(String(100), doc="Segundo celular de contacto en la escuela")
    contact_second_email = Column(String(512), doc="Segundo email de contacto de la escuela")
    contact_third_name = Column(String(512), doc="Segundo email de contacto de la escuela")
    contact_third_phone = Column(String(100), doc="Tercer telefono de la escuela")
    contact_third_cellphone = Column(String(100), doc="Segundo celular de contacto en la escuela")
    contact_third_email = Column(String(512), doc="Tercer email de contacto de la escuela")
    verify = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    created_at = Column("created", DateTime(timezone=True), default=datetime.now)
    updated_at = Column(
        "updated", 
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
