"""empty message

Revision ID: 1e8fb857a340
Revises: 
Create Date: 2019-01-29 12:31:41.550163

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e8fb857a340'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklisted',
    sa.Column('token_id', sa.Integer(), nullable=False),
    sa.Column('blacklisted_token', sa.String(length=150), nullable=True),
    sa.PrimaryKeyConstraint('token_id'),
    sa.UniqueConstraint('blacklisted_token')
    )
    op.create_table('outputs',
    sa.Column('output_id', sa.Integer(), nullable=False),
    sa.Column('output_name', sa.String(length=100), nullable=False),
    sa.Column('other_info', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('output_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=1000), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('activities',
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('activity_desc', sa.String(length=1000), nullable=False),
    sa.Column('activity_period', sa.Integer(), nullable=True),
    sa.Column('activity_progress', sa.Integer(), nullable=True),
    sa.Column('activity_patner', sa.String(length=100), nullable=True),
    sa.Column('under_output', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['under_output'], ['outputs.output_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('activity_id')
    )
    op.create_table('comments',
    sa.Column('actual_comment_id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(length=1000), nullable=False),
    sa.Column('author_user_id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.String(length=30), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.activity_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['author_user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('actual_comment_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    op.drop_table('activities')
    op.drop_table('users')
    op.drop_table('outputs')
    op.drop_table('blacklisted')
    # ### end Alembic commands ###
