"""Industry API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from wuxing_stock_app.modules.industry_engine import list_subcategories
from wuxing_stock_app import database


router = APIRouter()


@router.get("/subcategories")
def get_subcategories(category_id: str | None = Query(default=None)) -> dict[str, Any]:
    items = list_subcategories(category_id=category_id, has_access=False)
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "data": {"items": items, "count": len(items)},
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
    }


@router.get("/astock-boards")
def get_astock_boards(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    database.initialize_database()
    rows = database.fetch_all(
        """
        SELECT board_code, board_name, board_type, category, subcategory,
               main_element, secondary_element, confidence, reason, need_review
        FROM astock_board_wuxing_profiles
        ORDER BY need_review ASC, confidence DESC, board_code ASC
        LIMIT ?
        """,
        (limit,),
    )
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "data": {"items": rows, "count": len(rows)},
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
    }
