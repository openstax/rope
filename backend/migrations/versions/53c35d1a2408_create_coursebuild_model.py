"""Create CourseBuild model

Revision ID: 53c35d1a2408
Revises: aa205c6ae88f
Create Date: 2024-02-19 15:25:40.630245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53c35d1a2408'
down_revision = 'aa205c6ae88f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_build',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('instructor_firstname', sa.String(), nullable=False),
    sa.Column('instructor_lastname', sa.String(), nullable=False),
    sa.Column('instructor_email', sa.String(), nullable=False),
    sa.Column('course_name', sa.String(), nullable=False),
    sa.Column('course_shortname', sa.String(), nullable=False),
    sa.Column('course_category', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('course_enrollment_url', sa.String(), nullable=True),
    sa.Column('course_enrollment_key', sa.String(), nullable=True),
    sa.Column('school_district', sa.Integer(), nullable=False),
    sa.Column('academic_year', sa.String(), nullable=False),
    sa.Column('academic_year_short', sa.String(), nullable=False),
    sa.Column('base_course_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PROCESSING', 'COMPLETED', 'FAILED', name='coursebuildstatus'), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['user_account.id'], ),
    sa.ForeignKeyConstraint(['school_district'], ['school_district.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_shortname'),
    sa.UniqueConstraint('instructor_email', 'academic_year')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('course_build')
    # ### end Alembic commands ###