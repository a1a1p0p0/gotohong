"""User report history API."""

from __future__ import annotations

from typing import Any

import json

from fastapi import APIRouter, HTTPException, Query

from wuxing_stock_app import database
from wuxing_stock_app.backend.api.persistence import record_usage


router = APIRouter()


@router.get("/reports")
def get_user_reports(user_id: str = Query(...), limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    database.initialize_database()
    rows = database.fetch_all(
        """
        SELECT id, user_id, report_type, target_key, title, report_date, created_at
        FROM reports
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    record_usage("/api/user/reports", user_id, target_key=user_id)
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "data": {"items": rows, "count": len(rows)},
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
    }


@router.get("/report/{report_id}")
def get_user_report(report_id: int, user_id: str = Query(...)) -> dict[str, Any]:
    database.initialize_database()
    row = database.fetch_one(
        """
        SELECT id, user_id, report_type, target_key, title, report_date, payload_json, created_at
        FROM reports
        WHERE id = ? AND user_id = ?
        """,
        (report_id, user_id),
    )
    if row is None:
        raise HTTPException(status_code=404, detail="report not found")

    payload = json.loads(row.pop("payload_json"))
    record_usage("/api/user/report", user_id, target_key=str(report_id))
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "data": {"report": row, "payload": payload},
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
    }
