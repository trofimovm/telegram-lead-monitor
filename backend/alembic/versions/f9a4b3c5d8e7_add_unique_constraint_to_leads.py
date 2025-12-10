"""add unique constraint to leads table

Revision ID: f9a4b3c5d8e7
Revises: 6ebfcdb89d6a
Create Date: 2025-12-10 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9a4b3c5d8e7'
down_revision: Union[str, None] = '6ebfcdb89d6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create unique constraint to prevent duplicate leads from same message and rule
    op.create_unique_constraint(
        'uq_lead_tenant_message_rule',
        'leads',
        ['tenant_id', 'global_message_id', 'rule_id']
    )

    # Create performance indexes
    op.create_index('ix_leads_tenant_status', 'leads', ['tenant_id', 'status'])
    op.create_index('ix_leads_score', 'leads', ['score'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_leads_score', table_name='leads')
    op.drop_index('ix_leads_tenant_status', table_name='leads')

    # Drop unique constraint
    op.drop_constraint('uq_lead_tenant_message_rule', 'leads', type_='unique')
