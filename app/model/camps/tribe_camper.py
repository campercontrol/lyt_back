from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from utils.db import Base
from sqlalchemy.schema import UniqueConstraint

class TribeCamper(Base):
    __tablename__ = 'camps_tribecamper'
    __table_args__ = (
        UniqueConstraint('camper_id', 'tribecamp_id'),
    )
    id = Column("id", Integer, primary_key=True, nullable=False, autoincrement=True)
    camper_id = Column(ForeignKey("campers_camper.id", ondelete="cascade"), nullable=False, doc='Camper')
    tribecamp_id = Column(ForeignKey("camps_tribecamp.id"), nullable=False)
    created_at = Column("created", DateTime(timezone=True), default=datetime.now)
    updated_at = Column(
        "updated", 
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
