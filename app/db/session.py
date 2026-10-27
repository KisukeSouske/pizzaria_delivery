from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL, SQL_ECHO

# Cria a conexão com o banco de dados (SQLite por padrão)
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(bind=engine)

# Base de todos os models
Base = declarative_base()
