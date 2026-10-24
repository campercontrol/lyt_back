from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from utils.db import Base
from sqlalchemy.schema import UniqueConstraint

class TribeCamp(Base):
    __tablename__ = 'camps_tribecamp'
    __table_args__ = (
        UniqueConstraint('camp_id', 'tribe_id'),
    )
    id = Column("id", Integer, primary_key=True, nullable=False, autoincrement=True)
    camp_id = Column(ForeignKey("camps_camp.id"), nullable=False, doc='Campamento')
    tribe_id = Column(ForeignKey("camps_tribe.id"), nullable=False, doc="Id de la Tribu")
    created_at = Column("created", DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        "updated", 
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
