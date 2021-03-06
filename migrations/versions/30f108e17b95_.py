"""empty message

Revision ID: 30f108e17b95
Revises: 
Create Date: 2020-02-24 09:10:51.132913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30f108e17b95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sentiment', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('sentiment')

    # ### end Alembic commands ###
