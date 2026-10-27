from sqlalchemy import Boolean, Column, Integer, String

from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(100), nullable=False)
    email = Column("email", String(100), unique=True, nullable=False)
    senha = Column("senha", String(100), nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin
