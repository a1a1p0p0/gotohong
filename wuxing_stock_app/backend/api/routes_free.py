"""Free API routes for mobile pages."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from wuxing_stock_app.backend.api.persistence import record_usage
from wuxing_stock_app.modules.calendar_engine import get_period_element
from wuxing_stock_app.modules.industry_engine import get_category_profile, list_categories


router = APIRouter()


@router.get("/year")
def get_free_year(date_text: str | None = Query(default=None, alias="date")) -> dict[str, Any]:
    target_date = date_text or date.today().isoformat()
    try:
        analysis = get_period_element("year", target_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record_usage("/api/free/year", access_type="FREE_YEAR", target_key=target_date)
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": {"access_type": "FREE_YEAR", "access_granted": True},
        "data": {
            "title": "year element analysis",
            "period": analysis,
            "summary": "For element momentum observation only. Not investment advice.",
        },
    }


@router.get("/week")
def get_free_week(date_text: str | None = Query(default=None, alias="date")) -> dict[str, Any]:
    target_date = date_text or date.today().isoformat()
    try:
        analysis = get_period_element("week", target_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record_usage("/api/free/week", access_type="FREE_WEEK", target_key=target_date)
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": {"access_type": "FREE_WEEK", "access_granted": True},
        "data": {
            "title": "week element analysis",
            "period": analysis,
            "summary": "For weekly momentum observation only. Not investment advice.",
        },
    }


@router.get("/period")
def get_free_period(period_type: str = Query(...), date_text: str | None = Query(default=None, alias="date")) -> dict[str, Any]:
    target_date = date_text or date.today().isoformat()
    if period_type not in {"year", "month", "day"}:
        raise HTTPException(status_code=400, detail="period_type only supports year, month, day")
    try:
        analysis = get_period_element(period_type, target_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record_usage("/api/free/period", access_type="FREE_CATEGORY", target_key=f"{period_type}:{target_date}")
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": {"access_type": "FREE_CATEGORY", "access_granted": True},
        "data": {"period": analysis},
    }


@router.get("/categories")
def get_free_categories() -> dict[str, Any]:
    try:
        categories = list_categories()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    record_usage("/api/free/categories", access_type="FREE_CATEGORY", target_key="all")
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": {"access_type": "FREE_CATEGORY", "access_granted": True},
        "data": {
            "title": "free industry categories",
            "items": categories,
            "paid_hint": "Unlock subcategory reports for detailed momentum structure.",
        },
    }


@router.get("/category/{category_id}")
def get_free_category(category_id: str) -> dict[str, Any]:
    try:
        category = get_category_profile(category_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    record_usage("/api/free/category", access_type="FREE_CATEGORY", target_key=category_id)
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": {"access_type": "FREE_CATEGORY", "access_granted": True},
        "data": {
            "title": f"{category.get('category_name', category_id)} category analysis",
            "category": category,
            "paywall": {
                "required": True,
                "message": category.get("paid_hint", "Unlock to view detailed subcategory analysis."),
                "next_action": "unlock_subcategory",
            },
        },
    }
