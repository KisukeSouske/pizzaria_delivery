from sqlalchemy import Boolean, Column, Float, Integer, String

from app.db.session import Base


# Pizza (catálogo)
class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(100), unique=True, nullable=False)
    preco = Column("preco", Float, nullable=False)
    ativo = Column("ativo", Boolean, default=True)

    def __init__(self, nome, preco, ativo=True):
        self.nome = nome
        self.preco = preco
        self.ativo = ativo
