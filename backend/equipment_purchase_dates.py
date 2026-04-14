"""Shared logic for sample equipment.purchase_date values (CLI script + API)."""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models import Equipment


def _to_naive_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value.date()
    if isinstance(value, date):
        return value
    return None


def sample_purchase_date(created_at: date | datetime | None, row_id: int) -> date:
    """Stable pseudo-random date per row_id so re-runs are predictable for same ids."""
    rng = random.Random(row_id * 7919 + 104729)
    today = date.today()
    floor = date(2018, 1, 1)

    base = _to_naive_date(created_at)
    if base is not None:
        max_back = min(800, max(30, (base - floor).days))
        if max_back < 30:
            max_back = 30
        days_back = rng.randint(30, max_back)
        d = base - timedelta(days=days_back)
    else:
        span = max(30, (today - timedelta(days=60) - floor).days)
        d = floor + timedelta(days=rng.randint(0, span))

    if d < floor:
        d = floor + timedelta(days=rng.randint(0, 400))
    if d > today:
        d = today - timedelta(days=rng.randint(30, 400))
    return d


def fill_equipment_purchase_dates(db: Session, *, only_missing: bool = True) -> int:
    """
    Set sample purchase_date on equipment rows.
    If only_missing is True, only rows with NULL purchase_date are updated.
    Returns number of rows updated.
    """
    q = db.query(Equipment)
    if only_missing:
        q = q.filter(Equipment.purchase_date.is_(None))
    rows = q.order_by(Equipment.id).all()
    for e in rows:
        e.purchase_date = sample_purchase_date(e.created_at, e.id)
    db.commit()
    return len(rows)
