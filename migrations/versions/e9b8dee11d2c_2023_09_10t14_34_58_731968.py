"""2023-09-10T14:34:58.731968

Revision ID: e9b8dee11d2c
Revises: 
Create Date: 2023-09-10 14:34:58.966290

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e9b8dee11d2c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("surname", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=50), nullable=True),
        sa.Column("image_url", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_user_email"), "user", ["email"], unique=True, schema="public"
    )
    op.create_index(
        op.f("ix_public_user_id"), "user", ["id"], unique=False, schema="public"
    )
    op.create_table(
        "auth",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("refresh_token", sa.UUID(), nullable=False),
        sa.Column("expires_in", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["public.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_auth_refresh_token"),
        "auth",
        ["refresh_token"],
        unique=False,
        schema="public",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_public_auth_refresh_token"), table_name="auth", schema="public"
    )
    op.drop_table("auth", schema="public")
    op.drop_index(op.f("ix_public_user_id"), table_name="user", schema="public")
    op.drop_index(op.f("ix_public_user_email"), table_name="user", schema="public")
    op.drop_table("user", schema="public")
    # ### end Alembic commands ###
