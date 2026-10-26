from pydantic import BaseModel, Field


class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str

    class Config:
        from_attributes = True


class PizzaSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    preco: float = Field(gt=0)

    class Config:
        from_attributes = True


class PizzaUpdateSchema(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    preco: float | None = Field(default=None, gt=0)
    ativo: bool | None = None

    class Config:
        from_attributes = True


class PizzaResponseSchema(BaseModel):
    id: int
    nome: str
    preco: float
    ativo: bool

    class Config:
        from_attributes = True


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


class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True
