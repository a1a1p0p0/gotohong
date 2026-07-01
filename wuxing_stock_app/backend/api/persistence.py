"""Minimal API persistence helpers."""

from __future__ import annotations

import json
from typing import Any

from wuxing_stock_app import database


def record_usage(
    endpoint: str,
    user_id: str | None = None,
    access_type: str | None = None,
    target_key: str | None = None,
    status: str = "OK",
) -> None:
    database.initialize_database()
    database.execute(
        """
        INSERT INTO usage_logs (user_id, endpoint, access_type, target_key, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, endpoint, access_type, target_key, status),
    )


def save_report(report_type: str, user_id: str, target_key: str, payload: dict[str, Any]) -> int:
    database.initialize_database()
    _ensure_report_columns()
    title = str(payload.get("title", ""))
    report_date = str(payload.get("date", ""))
    database.execute(
        """
        INSERT INTO reports (user_id, report_type, target_key, title, report_date, payload_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, report_type, target_key, title, report_date, json.dumps(payload, ensure_ascii=False)),
    )
    row = database.fetch_one("SELECT last_insert_rowid() AS id")
    return int(row["id"]) if row else 0


def _ensure_report_columns() -> None:
    existing = {row["name"] for row in database.fetch_all("PRAGMA table_info(reports)")}
    if "title" not in existing:
        database.execute("ALTER TABLE reports ADD COLUMN title TEXT")
    if "report_date" not in existing:
        database.execute("ALTER TABLE reports ADD COLUMN report_date TEXT")
