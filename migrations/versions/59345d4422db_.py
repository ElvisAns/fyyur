"""empty message

Revision ID: 59345d4422db
Revises: f4062afff221
Create Date: 2022-08-08 12:52:41.223949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59345d4422db'
down_revision = 'f4062afff221'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'venue',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'venue',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
