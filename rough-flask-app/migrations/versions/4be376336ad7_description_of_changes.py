"""Description of changes

Revision ID: 4be376336ad7
Revises: ed8889cc9f52
Create Date: 2023-11-08 18:34:15.435625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4be376336ad7'
down_revision = 'ed8889cc9f52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('occupation', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('occupation')
        batch_op.drop_column('age')

    # ### end Alembic commands ###
