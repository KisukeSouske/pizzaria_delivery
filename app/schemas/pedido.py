from pydantic import BaseModel, Field


class ItemCarrinhoSchema(BaseModel):
    id_pizza: int
    quantidade: int = Field(gt=0)

    class Config:
        from_attributes = True


class CheckoutSchema(BaseModel):
    carrinho: int

    class Config:
        from_attributes = True


class ItemResponseSchema(BaseModel):
    id: int
    pizza: str | None
    quantidade: int
    preco_unitario: float
    preco: float

    class Config:
        from_attributes = True


class CarrinhoResponseSchema(BaseModel):
    id: int
    preco_total: float
    itens: list[ItemResponseSchema]

    class Config:
        from_attributes = True


class PedidoResponseSchema(BaseModel):
    id: int
    status: str
    preco_total: float
    itens: list[ItemResponseSchema]

    class Config:
        from_attributes = True


class PedidoResumoSchema(BaseModel):
    id: int
    status: str
    preco_total: float

    class Config:
        from_attributes = True
