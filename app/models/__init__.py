from app.models.pedido import Carrinho, ItemPedido, Pedido, StatusPedido
from app.models.pizza import Pizza
from app.models.usuario import Usuario

# Importar o pacote registra todas as tabelas em Base.metadata (usado pelo Alembic).
__all__ = ["Carrinho", "ItemPedido", "Pedido", "Pizza", "StatusPedido", "Usuario"]
