from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import criar_sessao, verificar_token
from app.models import Carrinho, ItemPedido, Pedido, Pizza, StatusPedido, Usuario
from app.schemas import (
    CarrinhoResponseSchema,
    CheckoutSchema,
    ItemCarrinhoSchema,
    PedidoResponseSchema,
    PedidoResumoSchema,
)
from app.services.orders import (
    buscar_carrinho,
    buscar_pedido,
    calcular_total,
    itens_do_carrinho,
    montar_carrinho,
    montar_pedido,
)

order_router = APIRouter(
    prefix="/orders", tags=["Orders"], dependencies=[Depends(verificar_token)]
)
SESSION_DEPENDENCY = Depends(criar_sessao)
USUARIO_DEPENDENCY = Depends(verificar_token)


@order_router.get("/", response_model=list[PedidoResumoSchema])
async def get_orders(
    usuario: Usuario = USUARIO_DEPENDENCY, session: Session = SESSION_DEPENDENCY
):
    """Lista os pedidos do usuário autenticado (o admin vê todos os pedidos)."""
    query = session.query(Pedido)
    if not usuario.admin:
        query = query.filter(Pedido.usuario == usuario.id)
    return query.order_by(Pedido.id).all()


@order_router.get("/pedido/{id_pedido}", response_model=PedidoResponseSchema)
async def ver_pedido(
    id_pedido: int,
    usuario: Usuario = USUARIO_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    pedido = buscar_pedido(id_pedido, usuario, session)
    return montar_pedido(pedido, session)


@order_router.post("/carrinho", status_code=201)
async def criar_carrinho(
    usuario: Usuario = USUARIO_DEPENDENCY, session: Session = SESSION_DEPENDENCY
):
    novo_carrinho = Carrinho(usuario=usuario.id)
    session.add(novo_carrinho)
    session.commit()
    return {"mensagem": "Carrinho criado", "id": novo_carrinho.id}


@order_router.get("/carrinho/{id_carrinho}", response_model=CarrinhoResponseSchema)
async def ver_carrinho(
    id_carrinho: int,
    usuario: Usuario = USUARIO_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    carrinho = buscar_carrinho(id_carrinho, usuario, session)
    return montar_carrinho(carrinho, session)


@order_router.post(
    "/carrinho/{id_carrinho}/itens",
    response_model=CarrinhoResponseSchema,
    status_code=201,
)
async def adicionar_item(
    id_carrinho: int,
    item_schema: ItemCarrinhoSchema,
    usuario: Usuario = USUARIO_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    carrinho = buscar_carrinho(id_carrinho, usuario, session)
    pizza = (
        session.query(Pizza)
        .filter(Pizza.id == item_schema.id_pizza, Pizza.ativo.is_(True))
        .first()
    )
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza não encontrada no cardápio.")

    item_existente = (
        session.query(ItemPedido)
        .filter(ItemPedido.carrinho == carrinho.id, ItemPedido.pizza == pizza.nome)
        .first()
    )
    if item_existente:
        item_existente.quantidade += item_schema.quantidade
        item_existente.preco = round(
            item_existente.preco_unitario * item_existente.quantidade, 2
        )
    else:
        # Nome e preço são copiados do catálogo para o item: o preço vem sempre
        # do servidor e o pedido mantém o valor da época, mesmo se o catálogo
        # mudar.
        item = ItemPedido(
            carrinho=carrinho.id,
            pizza=pizza.nome,
            preco_unitario=pizza.preco,
            quantidade=item_schema.quantidade,
        )
        session.add(item)
    session.flush()
    carrinho.preco_total = calcular_total(itens_do_carrinho(carrinho, session))
    session.commit()
    return montar_carrinho(carrinho, session)


@order_router.delete(
    "/carrinho/{id_carrinho}/itens/{id_item}", response_model=CarrinhoResponseSchema
)
async def remover_item(
    id_carrinho: int,
    id_item: int,
    usuario: Usuario = USUARIO_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    carrinho = buscar_carrinho(id_carrinho, usuario, session)
    item = (
        session.query(ItemPedido)
        .filter(ItemPedido.id == id_item, ItemPedido.carrinho == carrinho.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Item não encontrado neste carrinho."
        )
    session.delete(item)
    session.flush()
    carrinho.preco_total = calcular_total(itens_do_carrinho(carrinho, session))
    session.commit()
    return montar_carrinho(carrinho, session)


@order_router.post(
    "/pedido", response_model=PedidoResponseSchema, status_code=201
)  # Faz o checkout do carrinho e cria o pedido
async def checkout(
    checkout_schema: CheckoutSchema,
    usuario: Usuario = USUARIO_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    carrinho = buscar_carrinho(checkout_schema.carrinho, usuario, session)
    itens = itens_do_carrinho(carrinho, session)
    if not itens:
        raise HTTPException(status_code=400, detail="O carrinho está vazio.")

    pedido = Pedido(
        usuario=usuario.id,
        preco_total=calcular_total(itens),
        status=StatusPedido.AGUARDANDO_PGTO.value,
    )
    session.add(pedido)
    session.flush()

    # Os itens saem do carrinho e passam a pertencer ao pedido; o carrinho,
    # já consumido, é descartado. Tudo é confirmado em uma única transação.
    for item in itens:
        item.pedido = pedido.id
        item.carrinho = None
    session.flush()
    session.delete(carrinho)
    session.commit()
    return montar_pedido(pedido, session)


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    session: Session = SESSION_DEPENDENCY,
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorizção para fazer esta modificação.",
        )
    pedido.status = StatusPedido.CANCELADO.value
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido,
    }
