from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependences import criar_sessao
from schemas import CarrinhoSchema
from models import Pedido, Carrinho

order_router = APIRouter(prefix="/orders", tags=["Orders"])
SESSION_DEPENDENCY = Depends(criar_sessao)

@order_router.get("/")
async def get_orders():
    return {"message": "List of orders"}

@order_router.post("/carrinho")
async def criar_carrinho(pedido_schema: CarrinhoSchema, session: Session=SESSION_DEPENDENCY):
    novo_carrinho = Carrinho(usuario=pedido_schema.usuario)
    session.add(novo_carrinho)
    session.commit()
    return {"mensagem": "Carrinho criado", "id": novo_carrinho.id}