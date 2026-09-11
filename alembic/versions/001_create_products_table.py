"""create products table

Revision ID: 001_products
Revises: 
Create Date: 2026-09-11 12:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_products"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "products" in tables:
        # Table already exists (e.g. pre-existing database); safely record revision
        return

    jsonb_type = sa.JSON().with_variant(postgresql.JSONB, "postgresql")

    op.create_table(
        "products",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("brand", sa.String(), nullable=False, server_default="Hiljhil Roasters"),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("compare_at_price", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("in_stock", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("badge", sa.String(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tax_category", sa.String(), nullable=False, server_default="coffee_beans"),

        # Physical Dimensions & Clearances
        sa.Column("width_cm", sa.Float(), nullable=False, server_default="12.0"),
        sa.Column("height_cm", sa.Float(), nullable=False, server_default="20.0"),
        sa.Column("depth_cm", sa.Float(), nullable=False, server_default="6.0"),
        sa.Column("weight_kg", sa.Float(), nullable=True, server_default="0.25"),
        sa.Column("top_clearance_cm", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("side_clearance_cm", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("rear_clearance_cm", sa.Float(), nullable=False, server_default="0.0"),

        # Specialty Coffee Terroir & Craft
        sa.Column("roast_level", sa.String(), nullable=True),
        sa.Column("process_method", sa.String(), nullable=True),
        sa.Column("estate_name", sa.String(), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("elevation_m", sa.Integer(), nullable=True),
        sa.Column("varietal", sa.String(), nullable=True),
        sa.Column("resting_period_days", sa.Integer(), nullable=True),
        sa.Column("acidity", sa.String(), nullable=True),
        sa.Column("bitterness", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("best_enjoyed", sa.String(), nullable=True),

        # Media & Description
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("cutout_url", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),

        # Rich JSONB structures
        sa.Column("taste_notes", jsonb_type, nullable=True),
        sa.Column("recommended_brew_methods", jsonb_type, nullable=True),
        sa.Column("variants", jsonb_type, nullable=True),
        sa.Column("images", jsonb_type, nullable=True),

        # Legacy / String compatibility
        sa.Column("taste_notes_json", sa.Text(), nullable=True),
        sa.Column("specs_json", sa.Text(), nullable=True),

        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
        sa.UniqueConstraint("slug"),
    )

    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_slug", "products", ["slug"])
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_roast_level", "products", ["roast_level"])
    op.create_index("ix_products_process_method", "products", ["process_method"])
    op.create_index("ix_products_estate_name", "products", ["estate_name"])
    op.create_index("ix_products_price", "products", ["price"])


def downgrade() -> None:
    op.drop_index("ix_products_price", table_name="products")
    op.drop_index("ix_products_estate_name", table_name="products")
    op.drop_index("ix_products_process_method", table_name="products")
    op.drop_index("ix_products_roast_level", table_name="products")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")

