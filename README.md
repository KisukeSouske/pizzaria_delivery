# Pizzaria Delivery

API de delivery de pizzaria feita com FastAPI, SQLAlchemy e Alembic: cadastro e login (JWT), cardápio, carrinho e pedidos.

## Estrutura

```
app/
├── main.py             # cria o FastAPI e registra os routers
├── core/               # config.py (variáveis de ambiente) e security.py (JWT, bcrypt)
├── db/                 # session.py: engine, SessionLocal e Base
├── models/             # tabelas (usuario, pizza, pedido/carrinho/item)
├── schemas/            # schemas Pydantic de entrada e saída
├── api/
│   ├── dependencies.py # sessão do banco, usuário autenticado, admin
│   └── routes/         # auth.py, orders.py, pizzas.py
└── services/           # regras e consultas reutilizadas pelas rotas
alembic/                # migrations
tests/                  # testes automatizados
assets/                 # imagens do cardápio
frontend/               # interface React + TypeScript (ver frontend/README.md)
```

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # e ajuste SECRET_KEY
alembic upgrade head            # cria/atualiza o banco
uvicorn app.main:app --reload
```

A documentação interativa fica em http://localhost:8000/docs.

## Interface

Com a API no ar, em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

A interface sobe em http://localhost:5173 e fala com a API por um proxy do
Vite, então não é preciso liberar CORS. Detalhes em `frontend/README.md`.

## Migrations

```bash
alembic revision --autogenerate -m "descrição"
alembic upgrade head
```

A URL do banco vem de `DATABASE_URL` (padrão: `pizzaria.db` na raiz), a mesma usada pela API.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam um banco SQLite em memória e não tocam em `pizzaria.db`.
