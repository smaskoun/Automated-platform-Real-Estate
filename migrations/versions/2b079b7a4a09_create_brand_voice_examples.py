"""Create brand_voice_examples table

Revision ID: 2b079b7a4a09
Revises: f1df0c47e6d9
Create Date: 2024-09-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b079b7a4a09'
down_revision = 'f1df0c47e6d9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'brand_voice_examples',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('brand_voice_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['brand_voice_id'], ['brand_voices.id'], ondelete='CASCADE'),
    )


def downgrade():
    op.drop_table('brand_voice_examples')
