"""Add stats fields to User model

Revision ID: 530772dc8544
Revises: d9b28fa5412c
Create Date: 2025-01-10 14:24:44.659490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '530772dc8544'
down_revision = 'd9b28fa5412c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wins', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('losses', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('highest_winstreak', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('highest_winstreak')
        batch_op.drop_column('losses')
        batch_op.drop_column('wins')

    # ### end Alembic commands ###
