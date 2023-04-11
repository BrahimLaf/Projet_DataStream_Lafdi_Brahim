from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  # Importer declarative_base depuis le module sqlalchemy.ext
from sqlalchemy_utils import database_exists, create_database
from dotenv import dotenv_values, load_dotenv

load_dotenv()

CONFIG = dotenv_values(".env")   


    # Création de la base de données si elle n'existe pas
if not database_exists(f'mysql://{CONFIG["user"]}:{CONFIG["password"]}@{CONFIG["host"]}:{CONFIG["port"]}/{CONFIG["database"]}'):
    create_database(f'mysql://{CONFIG["user"]}:{CONFIG["password"]}@{CONFIG["host"]}:{CONFIG["port"]}/{CONFIG["database"]}')

    # On crée la chaîne de connexion
engine = create_engine(f'mysql://{CONFIG["user"]}:{CONFIG["password"]}@{CONFIG["host"]}:{CONFIG["port"]}/{CONFIG["database"]}?charset=utf8mb4')

    # Définition de la structure de la table RawLog
Base = declarative_base()
    
    
