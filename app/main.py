from fastapi import FastAPI

from app.api.routes.auth import auth_router
from app.api.routes.orders import order_router
from app.api.routes.pizzas import pizza_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(pizza_router)
