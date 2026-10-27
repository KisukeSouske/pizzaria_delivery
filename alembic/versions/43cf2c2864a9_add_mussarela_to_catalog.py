"""add mussarela to catalog

Revision ID: 43cf2c2864a9
Revises: b8dee240e46c
Create Date: 2026-10-27 16:12:44.201853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43cf2c2864a9'
down_revision: Union[str, Sequence[str], None] = 'b8dee240e46c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# A tabela já existe; esta referência leve serve só para o insert e o delete.
pizzas = sa.table(
    'pizzas',
    sa.column('nome', sa.String),
    sa.column('preco', sa.Float),
    sa.column('ativo', sa.Boolean),
)


def upgrade() -> None:
    """Acrescenta a Mussarela ao cardápio."""
    op.bulk_insert(pizzas, [
        {'nome': 'Mussarela', 'preco': 35.50, 'ativo': True},
    ])


def downgrade() -> None:
    """Tira a Mussarela do cardápio."""
    op.execute(pizzas.delete().where(pizzas.c.nome == 'Mussarela'))
