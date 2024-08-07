"""Update course_category to course_category_id

Revision ID: 8136a365e462
Revises: ece1292c9bdc
Create Date: 2024-05-03 10:37:49.115436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8136a365e462'
down_revision = 'ece1292c9bdc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('course_build', column_name='course_category', new_column_name='course_category_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('course_build', column_name='course_category_id', new_column_name='course_category')
    # ### end Alembic commands ###
