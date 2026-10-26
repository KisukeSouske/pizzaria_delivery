import enum
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Float,
    Enum,
)
from sqlalchemy.orm import declarative_base

# Cria a conexão com o banco de dados SQLite
db = create_engine("sqlite:///pizzaria.db", echo=True)

# Cria a base de dados
Base = declarative_base()


# O status é gravado como texto na coluna `pedidos.status` (String)
class StatusPedido(str, enum.Enum):
    AGUARDANDO_PGTO = "AGUARDANDO_PGTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"


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

    def __init__(self, carrinho, pizza, preco_unitario, quantidade):
        self.carrinho = carrinho
        self.pizza = pizza
        self.preco_unitario = preco_unitario
        self.quantidade = quantidade
        self.preco = round(preco_unitario * quantidade, 2)
