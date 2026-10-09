import enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import declarative_base

# Cria a conexão com o banco de dados SQLite
db = create_engine("sqlite:///pizzaria.db", echo=True)

# Cria a base de dados
Base = declarative_base()

""" class STATUS_PEDIDO(enum.Enum):
    AGUARDANDO_PGTO = 1
    FINALIZADO = 2
    CANCELADO = 3 """

""" class PIZZA(enum.Enum):
    PEPERONI = 1
    CALABRESA = 2
    PORTUGUESA = 3 """

# Usuario
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


# Pedido
class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String, nullable=False)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco_total = Column("preco_total", Float)

    def __init__(self, usuario, preco_total, status):
        self.status = status
        self.usuario = usuario
        self.preco_total = preco_total

# Carrinho
class Carrinho(Base):
    __tablename__ = "carrinhos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco_total = Column("preco_total", Float)

    def __init__(self, usuario, preco_total=0):
        self.usuario = usuario
        self.preco_total = preco_total


# ItensPedido
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    carrinho = Column("carrinho", ForeignKey("carrinhos.id"))
    pedido = Column("pedido", ForeignKey("pedidos.id"))
    preco_unitario = Column("preco_unitario", Float, nullable=False)
    quantidade = Column("quantidade", Integer, nullable=False)
    preco = Column("preco", Float, nullable=False)
    pizza = Column("pizza", String)

    def __init__(self, carrinho, preco_unitario, quantidade):
        self.carrinho = carrinho
        self.preco_unitario = preco_unitario
        self.quantidade = quantidade
        self.preco = preco_unitario * quantidade
