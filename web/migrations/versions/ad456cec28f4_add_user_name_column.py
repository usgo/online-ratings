"""Add User.name column

Revision ID: ad456cec28f4
Revises: d767d9266a19
Create Date: 2016-11-21 03:03:08.967762

"""

# revision identifiers, used by Alembic.
revision = 'ad456cec28f4'
down_revision = 'd767d9266a19'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('myuser', sa.Column('name', sa.String(length=255), nullable=False, server_default=''))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('myuser', 'name')
    ### end Alembic commands ###
