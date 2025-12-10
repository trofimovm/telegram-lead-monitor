"""remove old tables

Revision ID: d5e8f2a3b9c1
Revises: c4f2a1d8e9b0
Create Date: 2025-12-04 15:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5e8f2a3b9c1'
down_revision: Union[str, None] = 'c4f2a1d8e9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Удаление старых таблиц messages и sources после миграции на глобальную архитектуру.
    """
    # 1. Удалить FK constraint message_id из таблицы leads
    op.drop_constraint('leads_message_id_fkey', 'leads', type_='foreignkey')

    # 2. Удалить колонку message_id из таблицы leads
    op.drop_column('leads', 'message_id')

    # 3. Удалить таблицу messages (все зависимости уже удалены)
    op.drop_table('messages')

    # 4. Удалить таблицу sources (все зависимости уже удалены через channel_subscriptions)
    op.drop_table('sources')


def downgrade() -> None:
    """
    Откат миграции - восстановление таблиц.
    ВНИМАНИЕ: Данные не восстанавливаются!
    """
    # Создать таблицу sources
    op.create_table(
        'sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tg_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('subscribers_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['telegram_account_id'], ['telegram_accounts.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sources_tenant_id', 'sources', ['tenant_id'])
    op.create_index('ix_sources_tg_id', 'sources', ['tg_id'])

    # Создать таблицу messages
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tg_message_id', sa.BigInteger(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('author_tg_id', sa.BigInteger(), nullable=True),
        sa.Column('author_username', sa.String(length=255), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_messages_source_id', 'messages', ['source_id'])
    op.create_index('ix_messages_tg_message_id', 'messages', ['tg_message_id'])
    op.create_index('ix_messages_sent_at', 'messages', ['sent_at'])

    # Добавить обратно колонку message_id в leads
    op.add_column('leads', sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('leads_message_id_fkey', 'leads', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
