import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from utils.db import Base

class Location(Base):
    __tablename__ = 'camps_location'

    uid = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        index=True,
    )
    id =Column("id", Integer(), primary_key=True, nullable=False, autoincrement=True) 
    name = Column("name", String(512), nullable=False, doc = 'Nombre de la sede')
    phone = Column("phone", String(100), nullable=False, doc= 'Telefono')
    email = Column("email", String(512), nullable=False, doc= 'Email de contacto')
    contact = Column("contact", String(512), nullable=False, doc= 'Persona de contacto')
    address = Column("address", Text, doc= 'Dirección')
    url = Column("url", String(512), doc= 'Pagina web')
    active = Column("active", Boolean, nullable=False, doc= 'Activa')
    created_at = Column("created", DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        "updated", 
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
