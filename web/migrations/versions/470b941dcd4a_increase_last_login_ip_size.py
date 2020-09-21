"""increase last login ip size

Revision ID: 470b941dcd4a
Revises: 31163dd1dbbb
Create Date: 2020-09-04 14:46:58.543859

"""

# revision identifiers, used by Alembic.
revision = '470b941dcd4a'
down_revision = '31163dd1dbbb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    for column in ['last_login_ip', 'current_login_ip']:
        op.alter_column('myuser', column,
                        existing_type=sa.String(25),
                        type_=sa.String(45))

def downgrade():
    for column in ['last_login_ip', 'current_login_ip']:
        op.alter_column('myuser', column,
                        existing_type=sa.String(45),
                        type_=sa.String(25))
