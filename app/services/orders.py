from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Carrinho, ItemPedido, Pedido, Usuario


def buscar_carrinho(id_carrinho: int, usuario: Usuario, session: Session) -> Carrinho:
    """Retorna o carrinho, garantindo que ele pertence ao usuário autenticado."""
    carrinho = session.query(Carrinho).filter(Carrinho.id == id_carrinho).first()
    if not carrinho:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado.")
    if carrinho.usuario != usuario.id:
        raise HTTPException(
            status_code=403, detail="Você não tem acesso a este carrinho."
        )
    return carrinho


def buscar_pedido(id_pedido: int, usuario: Usuario, session: Session) -> Pedido:
    """Retorna o pedido, se for do usuário autenticado (ou se ele for admin)."""
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(
            status_code=403, detail="Você não tem acesso a este pedido."
        )
    return pedido


def itens_do_carrinho(carrinho: Carrinho, session: Session) -> list[ItemPedido]:
    return (
        session.query(ItemPedido)
        .filter(ItemPedido.carrinho == carrinho.id)
        .order_by(ItemPedido.id)
        .all()
    )


def itens_do_pedido(pedido: Pedido, session: Session) -> list[ItemPedido]:
    return (
        session.query(ItemPedido)
        .filter(ItemPedido.pedido == pedido.id)
        .order_by(ItemPedido.id)
        .all()
    )


def calcular_total(itens: list[ItemPedido]) -> float:
    return round(sum(item.preco for item in itens), 2)


def montar_carrinho(carrinho: Carrinho, session: Session) -> dict:
    return {
        "id": carrinho.id,
        "preco_total": carrinho.preco_total,
        "itens": itens_do_carrinho(carrinho, session),
    }


def montar_pedido(pedido: Pedido, session: Session) -> dict:
    return {
        "id": pedido.id,
        "status": pedido.status,
        "preco_total": pedido.preco_total,
        "itens": itens_do_pedido(pedido, session),
    }
