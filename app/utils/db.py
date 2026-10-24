import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())
user = os.getenv("DB_USER", "")
password = os.getenv("DB_PASS", "")
host = os.getenv("DB_HOST", "")
port = os.getenv("DB_PORT", "")
db = os.getenv("DB_NAME", "")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
#SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c timezone=America/Mexico_City"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def db_mapping_rows_to_dict(query):
    """Convierte una consulta  sqlalchemy.engine.row.Row a un diccionario"""
    result = []
    for row in query:
        result.append(row._mapping)
    return result
