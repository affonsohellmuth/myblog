# api/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração da conexão PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Criar engine do SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Criar sessão local para cada operação no banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos
Base = declarative_base()

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()