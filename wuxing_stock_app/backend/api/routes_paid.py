"""Paid API placeholders with local unlock-code checks."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from wuxing_stock_app.backend.api.persistence import record_usage, save_report
from wuxing_stock_app.modules.auth_engine import has_access, use_unlock_code
from wuxing_stock_app.modules.calendar_engine import get_period_element
from wuxing_stock_app.modules.industry_engine import get_subcategory_profile
from wuxing_stock_app.modules.ranking_engine import rank_industries


router = APIRouter()


class PaidDayRequest(BaseModel):
    date: str = Field(..., examples=["2026-06-29"])
    user_id: str
    unlock_code: str | None = None


class PaidSubcategoryRequest(BaseModel):
    subcategory_id: str
    date: str = Field(..., examples=["2026-06-29"])
    user_id: str
    unlock_code: str | None = None


class PaidRankingRequest(BaseModel):
    period_type: Literal["month", "week", "day"]
    ranking_type: Literal["favorable", "balanced"]
    date: str = Field(..., examples=["2026-06-29"])
    user_id: str
    unlock_code: str | None = None


@router.post("/day")
def post_paid_day(payload: PaidDayRequest) -> dict[str, Any]:
    access = _check_access("PAID_DAY", payload.date, payload.unlock_code)
    if not access["access_granted"]:
        record_usage("/api/paid/day", payload.user_id, access["access_type"], access["target_key"], "PAYWALL")
        return _locked_response(access, "Daily report requires unlock code.")

    period = get_period_element("day", payload.date)
    response = {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": access,
        "data": {
            "report_type": "paid_day",
            "title": "daily element report",
            "date": payload.date,
            "period": period,
            "sections": [
                {"title": "core momentum", "content": period["description"]},
                {"title": "risk notice", "content": "Observation only. Not investment advice."},
            ],
        },
    }
    save_report("paid_day", payload.user_id, payload.date, response["data"])
    record_usage("/api/paid/day", payload.user_id, access["access_type"], access["target_key"], "OK")
    return response


@router.post("/subcategory")
def post_paid_subcategory(payload: PaidSubcategoryRequest) -> dict[str, Any]:
    access = _check_access("PAID_SUBCATEGORY_SINGLE", payload.subcategory_id, payload.unlock_code)
    if not access["access_granted"]:
        record_usage("/api/paid/subcategory", payload.user_id, access["access_type"], access["target_key"], "PAYWALL")
        return _locked_response(access, "Subcategory report requires unlock code.")

    profile = get_subcategory_profile(payload.subcategory_id, has_access=True)
    day_profile = get_period_element("day", payload.date)
    response = {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": access,
        "data": {
            "report_type": "paid_subcategory",
            "title": f"{profile['subcategory_name']} subcategory report",
            "date": payload.date,
            "industry": profile,
            "time_profile": day_profile,
            "sections": [
                {"title": "momentum behavior", "content": profile.get("behavior_description", "")},
                {"title": "risk notice", "content": "Observation only. Not investment advice."},
            ],
        },
    }
    save_report("paid_subcategory", payload.user_id, payload.subcategory_id, response["data"])
    record_usage("/api/paid/subcategory", payload.user_id, access["access_type"], access["target_key"], "OK")
    return response


@router.post("/ranking")
def post_paid_ranking(payload: PaidRankingRequest) -> dict[str, Any]:
    access_type = f"PAID_{payload.period_type.upper()}_RANKING"
    target_key = f"{payload.period_type}:{payload.ranking_type}:{payload.date}"
    access = _check_access(access_type, target_key, payload.unlock_code)
    if not access["access_granted"]:
        preview = rank_industries(payload.period_type, payload.date, payload.ranking_type)[:1]
        locked = _locked_response(access, "Top 5 ranking requires unlock code.")
        locked["data"] = {
            "report_type": "paid_ranking_preview",
            "preview_items": preview,
            "visible_count": len(preview),
            "locked_count": max(0, 5 - len(preview)),
        }
        record_usage("/api/paid/ranking", payload.user_id, access["access_type"], access["target_key"], "PAYWALL")
        return locked

    items = rank_industries(payload.period_type, payload.date, payload.ranking_type)
    response = {
        "success": True,
        "code": "OK",
        "message": "ok",
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": access,
        "data": {
            "report_type": "paid_ranking",
            "title": _ranking_title(payload.period_type, payload.ranking_type),
            "period_type": payload.period_type,
            "ranking_type": payload.ranking_type,
            "date": payload.date,
            "items": items,
            "risk_notice": "Ranking expresses element momentum matching only. Not investment advice.",
        },
    }
    save_report("paid_ranking", payload.user_id, target_key, response["data"])
    record_usage("/api/paid/ranking", payload.user_id, access["access_type"], access["target_key"], "OK")
    return response


def _check_access(access_type: str, target_key: str, unlock_code: str | None) -> dict[str, Any]:
    granted = has_access(access_type, target_key, unlock_code)
    if granted and unlock_code:
        use_unlock_code(unlock_code, access_type, target_key)
    return {
        "access_type": access_type,
        "target_key": target_key,
        "access_granted": granted,
        "unlock_code_checked": bool(unlock_code),
    }


def _locked_response(access: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "success": False,
        "code": "PAYWALL_REQUIRED",
        "message": message,
        "data": None,
        "risk_notice": "Observation only. Not investment advice.",
        "access": access,
        "paywall": {
            "required": True,
            "message": message,
            "next_action": "verify_unlock_code",
        },
        "example": {
            "title": "example report structure",
            "sections": ["momentum behavior", "time relation", "element relation", "risk notice"],
        },
    }


def _ranking_title(period_type: str, ranking_type: str) -> str:
    period_label = {"month": "month", "week": "week", "day": "day"}[period_type]
    ranking_label = {"favorable": "favorable industries", "balanced": "balanced industries"}[ranking_type]
    return f"{period_label} {ranking_label} TOP 5"
