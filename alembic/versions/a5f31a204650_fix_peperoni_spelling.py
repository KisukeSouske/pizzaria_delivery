"""fix peperoni spelling

Revision ID: a5f31a204650
Revises: 43cf2c2864a9
Create Date: 2026-10-27 16:31:09.774412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5f31a204650'
down_revision: Union[str, Sequence[str], None] = '43cf2c2864a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


pizzas = sa.table('pizzas', sa.column('nome', sa.String))


def upgrade() -> None:
    """Corrige a grafia do sabor no catálogo.

    `itens_pedido.pizza` guarda de propósito o nome da época do pedido, então os
    pedidos já feitos não são tocados.
    """
    op.execute(
        pizzas.update().where(pizzas.c.nome == 'Peperoni').values(nome='Pepperoni')
    )


def downgrade() -> None:
    """Volta para a grafia antiga."""
    op.execute(
        pizzas.update().where(pizzas.c.nome == 'Pepperoni').values(nome='Peperoni')
    )
