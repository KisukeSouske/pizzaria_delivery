from pydantic import BaseModel, Field


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
