from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Date, Text
from sqlalchemy.dialects.mysql import FLOAT as MY_SQL_FLOAT, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from dotenv import dotenv_values


CONFIG = dotenv_values(".env")

Base = declarative_base()

# Définir les modèles de table CleanLog et RowLog
class CleanLog(Base):
    __tablename__ = "clean_log"
    # Définir les colonnes et leurs types de données
    id = Column(String(255), primary_key=True, nullable=False)
    timestamp = Column(String(255), nullable=True)
    year = Column(String(255), nullable=True)
    month = Column(String(255), nullable=True)
    day = Column(String(255), nullable=True)
    day_of_week = Column(String(255), nullable=True)
    hourminuteseconde = Column(String(255), nullable=True)
    ip = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
#    session = Column(String(255), nullable=True)
    user = Column(String(255), nullable=True)
    is_email = Column(String(255), nullable=True)
    Domaine = Column(String(255), nullable=True)
    Methode = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    schema = Column(String(255), nullable=True)
    host = Column(String(255), nullable=True)
    rest_version = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    status_verbose = Column(String(255), nullable=True)
    size_bytes = Column(String(255), nullable=True)
    size_kilo_bytes = Column(String(255), nullable=True)
    size_mega_bytes = Column(String(255), nullable=True)

                             
                             
                             
class RowLog(Base):
    __tablename__ = "raw_log"
    # Définir les colonnes et leurs types de données
    id = Column(String(255), primary_key=True, nullable=False)
    timestamp = Column(String(255), nullable=False)
    log = Column(Text, nullable=False)

# Créer les tables dans la base de données
engine = create_engine(f'mysql://{CONFIG["user"]}:{CONFIG["password"]}@{CONFIG["host"]}:{CONFIG["port"]}/{CONFIG["database"]}?charset=utf8mb4')
Base.metadata.create_all(engine)