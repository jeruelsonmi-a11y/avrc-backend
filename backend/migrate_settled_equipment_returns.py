#!/usr/bin/env python3
"""
Adds settled flag on equipment_returns and links notifications to a specific return.
Run once: python migrate_settled_equipment_returns.py
"""

from sqlalchemy import inspect

from database import engine


def migrate():
    inspector = inspect(engine)
    er_cols = {c["name"] for c in inspector.get_columns("equipment_returns")}
    notif_cols = {c["name"] for c in inspector.get_columns("notifications")}

    with engine.begin() as conn:
        if "settled" not in er_cols:
            conn.exec_driver_sql(
                "ALTER TABLE equipment_returns ADD COLUMN settled TINYINT(1) NOT NULL DEFAULT 0"
            )
            print("[OK] Added equipment_returns.settled")
        else:
            print("[OK] equipment_returns.settled already exists")

        if "equipment_return_id" not in notif_cols:
            conn.exec_driver_sql(
                "ALTER TABLE notifications ADD COLUMN equipment_return_id INT NULL"
            )
            print("[OK] Added notifications.equipment_return_id")
        else:
            print("[OK] notifications.equipment_return_id already exists")


if __name__ == "__main__":
    print("migrate_settled_equipment_returns...")
    migrate()
    print("Done.")
