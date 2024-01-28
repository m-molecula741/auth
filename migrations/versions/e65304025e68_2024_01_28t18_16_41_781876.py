"""2024-01-28T18:16:41.781876

Revision ID: e65304025e68
Revises: e9b8dee11d2c
Create Date: 2024-01-28 18:16:42.185860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e65304025e68'
down_revision = 'e9b8dee11d2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('auth_user_id_fkey', 'auth', type_='foreignkey')
    op.create_foreign_key(None, 'auth', 'user', ['user_id'], ['id'], source_schema='public', referent_schema='public', ondelete='CASCADE')
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('user', 'surname',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.drop_index('ix_public_user_id', table_name='user')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_public_user_id', 'user', ['id'], unique=False)
    op.alter_column('user', 'surname',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.drop_constraint(None, 'auth', schema='public', type_='foreignkey')
    op.create_foreign_key('auth_user_id_fkey', 'auth', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###