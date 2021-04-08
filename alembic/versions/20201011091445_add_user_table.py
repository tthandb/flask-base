"""add user table

Revision ID: 229c0c71205b
Revises: 
Create Date: 2020-10-11 09:14:45.384226

"""
import os
import sys
from alembic import op
import sqlalchemy as sa
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
from base import auto_build_model # noqa


# revision identifiers, used by Alembic.
revision = '229c0c71205b'
down_revision = None
branch_labels = None
depends_on = None


@auto_build_model('users')
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('status', sa.String, nullable=True),
        sa.Column('first_name', sa.String, nullable=True),
        sa.Column('last_name', sa.String, nullable=True),
        sa.Column('email', sa.String, nullable=True, index=True),
        sa.Column('password', sa.String, nullable=True),
        sa.Column('tokens', sa.JSON, nullable=True),
        sa.Column('configs', sa.JSON, nullable=True),
        sa.Column(
            'timezone', sa.Float, nullable=True, default=-8
        ),
        sa.Column('city', sa.String, nullable=True),
        sa.Column('zipcode', sa.String, nullable=True),
        sa.Column('country', sa.String, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True)
    )
    op.create_unique_constraint(
        'uniq_email', 'users', ['email']
    )


def downgrade():
    op.drop_table('users')
