"""Alembic script template."""
from typing import Any

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = "initial_migration"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade(name: str = "") -> None:
    if name:
        pass

    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create simulations table
    op.create_table(
        "simulations",
        sa.Column("simulation_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("experiment_name", sa.String(length=255), nullable=False),
        sa.Column("run_name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("ecological_zone", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "location",
            Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=False,
        ),
        sa.Column("geohash", sa.String(length=50), nullable=True),
        sa.Column("crop", sa.String(length=100), nullable=False),
        sa.Column("cultivar", sa.String(length=255), nullable=True),
        sa.Column("irrigation", sa.String(length=100), nullable=True),
        sa.Column("nitrogen_level", sa.String(length=100), nullable=True),
        sa.Column("planting_stage", sa.String(length=100), nullable=True),
        sa.Column("planting_date", sa.Date(), nullable=True),
        sa.Column("maturity_date", sa.Date(), nullable=True),
        sa.Column("harvest_date", sa.Date(), nullable=True),
        sa.Column("simulation_year", sa.Integer(), nullable=False),
        sa.Column("harvest_area", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("simulation_id"),
    )

    # Create indexes
    op.create_index(op.f("ix_simulations_country"), "simulations", ["country"], unique=False)
    op.create_index(op.f("ix_simulations_state"), "simulations", ["state"], unique=False)
    op.create_index(op.f("ix_simulations_district"), "simulations", ["district"], unique=False)
    op.create_index(op.f("ix_simulations_crop"), "simulations", ["crop"], unique=False)
    op.create_index(op.f("ix_simulations_cultivar"), "simulations", ["cultivar"], unique=False)
    op.create_index(op.f("ix_simulations_simulation_year"), "simulations", ["simulation_year"], unique=False)
    op.create_index(op.f("ix_simulations_ecological_zone"), "simulations", ["ecological_zone"], unique=False)
    op.create_index("idx_simulation_location", "simulations", ["location"], unique=False, postgresql_using="gist")

    # Create simulation_outputs table
    op.create_table(
        "simulation_outputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("variable_code", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.simulation_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(op.f("ix_simulation_outputs_simulation_id"), "simulation_outputs", ["simulation_id"], unique=False)
    op.create_index(op.f("ix_simulation_outputs_variable_code"), "simulation_outputs", ["variable_code"], unique=False)
    op.create_index(
        "idx_output_simulation_variable",
        "simulation_outputs",
        ["simulation_id", "variable_code"],
        unique=False,
    )


def downgrade(name: str = "") -> None:
    if name:
        pass

    # Drop indexes
    op.drop_index("idx_output_simulation_variable", table_name="simulation_outputs")
    op.drop_index(op.f("ix_simulation_outputs_variable_code"), table_name="simulation_outputs")
    op.drop_index(op.f("ix_simulation_outputs_simulation_id"), table_name="simulation_outputs")

    # Drop simulation_outputs table
    op.drop_table("simulation_outputs")

    # Drop indexes
    op.drop_index("idx_simulation_location", table_name="simulations")
    op.drop_index(op.f("ix_simulations_ecological_zone"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_simulation_year"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_cultivar"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_crop"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_district"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_state"), table_name="simulations")
    op.drop_index(op.f("ix_simulations_country"), table_name="simulations")

    # Drop simulations table
    op.drop_table("simulations")

    # Disable PostGIS extension (optional, may cause issues)
    # op.execute("DROP EXTENSION IF EXISTS postgis")
