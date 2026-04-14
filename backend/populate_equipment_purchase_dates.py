#!/usr/bin/env python3
"""
Fill equipment.purchase_date with plausible sample dates.

By default only rows where purchase_date IS NULL are updated (safe for real data).
Use --all to overwrite every equipment row.

Requires .env (same as backend) and purchase_date column on equipment.
"""

from __future__ import annotations

import argparse

from database import SessionLocal
from equipment_purchase_dates import sample_purchase_date
from models import Equipment


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate sample purchase_date on equipment.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update every equipment row, not only NULL purchase_date.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        q = db.query(Equipment)
        if not args.all:
            q = q.filter(Equipment.purchase_date.is_(None))
        rows = q.order_by(Equipment.id).all()
        if not rows:
            print("No matching equipment rows to update.")
            return

        print(f"Updating {len(rows)} equipment row(s) with sample purchase_date...")
        for e in rows:
            e.purchase_date = sample_purchase_date(e.created_at, e.id)
            print(f"  id={e.id} {e.name!r} item#{e.item_number} -> {e.purchase_date}")
        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
