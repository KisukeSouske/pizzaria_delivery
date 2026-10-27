from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import criar_sessao, verificar_admin
from app.models import Pizza, Usuario
from app.schemas import PizzaResponseSchema, PizzaSchema, PizzaUpdateSchema

pizza_router = APIRouter(prefix="/pizzas", tags=["Pizzas"])
SESSION_DEPENDENCY = Depends(criar_sessao)
ADMIN_DEPENDENCY = Depends(verificar_admin)


def verificar_nome_disponivel(
    nome: str, session: Session, ignorar_id: int | None = None
):
    """Impede dois sabores com o mesmo nome, sem diferenciar maiúsculas de minúsculas."""
    query = session.query(Pizza).filter(func.lower(Pizza.nome) == nome.lower())
    if ignorar_id is not None:
        query = query.filter(Pizza.id != ignorar_id)
    if query.first():
        raise HTTPException(
            status_code=400, detail="Já existe uma pizza com este nome no catálogo."
        )


@pizza_router.get("/", response_model=list[PizzaResponseSchema])
async def listar_pizzas(session: Session = SESSION_DEPENDENCY):
    """Cardápio público: apenas as pizzas disponíveis para pedido."""
    return session.query(Pizza).filter(Pizza.ativo.is_(True)).order_by(Pizza.nome).all()


@pizza_router.get("/todas", response_model=list[PizzaResponseSchema])
async def listar_todas_pizzas(
    admin: Usuario = ADMIN_DEPENDENCY, session: Session = SESSION_DEPENDENCY
):
    """Catálogo completo, incluindo as pizzas desativadas (somente admin)."""
    return session.query(Pizza).order_by(Pizza.nome).all()


@pizza_router.post("/", response_model=PizzaResponseSchema, status_code=201)
async def criar_pizza(
    pizza_schema: PizzaSchema,
    admin: Usuario = ADMIN_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    verificar_nome_disponivel(pizza_schema.nome, session)
    nova_pizza = Pizza(nome=pizza_schema.nome, preco=pizza_schema.preco)
    session.add(nova_pizza)
    session.commit()
    return nova_pizza


@pizza_router.patch("/{id_pizza}", response_model=PizzaResponseSchema)
async def atualizar_pizza(
    id_pizza: int,
    pizza_schema: PizzaUpdateSchema,
    admin: Usuario = ADMIN_DEPENDENCY,
    session: Session = SESSION_DEPENDENCY,
):
    """Altera nome, preço e/ou disponibilidade. Pizza desativada sai do cardápio."""
    pizza = session.query(Pizza).filter(Pizza.id == id_pizza).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza não encontrada.")
    alteracoes = pizza_schema.model_dump(exclude_none=True)
    if "nome" in alteracoes:
        verificar_nome_disponivel(alteracoes["nome"], session, ignorar_id=pizza.id)
    for campo, valor in alteracoes.items():
        setattr(pizza, campo, valor)
    session.commit()
    return pizza
