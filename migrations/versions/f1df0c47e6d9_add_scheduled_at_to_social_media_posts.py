"""Add scheduled_at to social_media_posts

Revision ID: f1df0c47e6d9
Revises: 000000000000
Create Date: 2024-08-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1df0c47e6d9'
down_revision = '000000000000'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('social_media_posts', sa.Column('scheduled_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('social_media_posts', 'scheduled_at')

