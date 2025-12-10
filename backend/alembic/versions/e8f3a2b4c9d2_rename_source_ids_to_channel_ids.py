"""rename source_ids to channel_ids in rules

Revision ID: e8f3a2b4c9d2
Revises: d5e8f2a3b9c1
Create Date: 2025-12-04 21:39:17.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e8f3a2b4c9d2'
down_revision: Union[str, None] = 'd5e8f2a3b9c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Переименовать source_ids в channel_ids в таблице rules.

    Поскольку старые source_ids ссылались на удаленную таблицу sources,
    мы обнуляем все значения при переименовании.
    """
    # 1. Обнулить все source_ids (они больше не валидны)
    op.execute("UPDATE rules SET source_ids = NULL")

    # 2. Переименовать колонку
    op.alter_column('rules', 'source_ids', new_column_name='channel_ids')


def downgrade() -> None:
    """
    Откат миграции - переименовать обратно в source_ids.
    """
    op.alter_column('rules', 'channel_ids', new_column_name='source_ids')
