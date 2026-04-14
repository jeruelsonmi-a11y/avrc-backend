#!/usr/bin/env python3
"""Add purchase_date (DATE NULL) to equipment table."""

from sqlalchemy import inspect

from database import engine


def migrate():
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("equipment")}
    with engine.begin() as conn:
        if "purchase_date" not in cols:
            conn.exec_driver_sql("ALTER TABLE equipment ADD COLUMN purchase_date DATE NULL")
            print("[OK] Added equipment.purchase_date")
        else:
            print("[OK] equipment.purchase_date already exists")


if __name__ == "__main__":
    print("migrate_equipment_purchase_date...")
    migrate()
    print("Done.")
