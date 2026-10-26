from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from utils.db import Base

class Tribe(Base):
    __tablename__ = 'camps_tribe'
    id = Column("id", Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column("name", String(512), doc = 'Nombre de la sede')
    created_at = Column("created", DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        "updated", 
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
