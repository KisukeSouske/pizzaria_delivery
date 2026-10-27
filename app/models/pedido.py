import enum

from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.db.session import Base


# O status é gravado como texto na coluna `pedidos.status` (String)
class StatusPedido(str, enum.Enum):
    AGUARDANDO_PGTO = "AGUARDANDO_PGTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"


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
