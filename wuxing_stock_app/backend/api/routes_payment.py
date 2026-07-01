"""Local payment and unlock-code API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from wuxing_stock_app.backend.api.persistence import record_usage
from wuxing_stock_app.modules.payment_engine import confirm_payment, create_payment_order
from wuxing_stock_app.modules.auth_engine import has_access


router = APIRouter()


class VerifyUnlockCodeRequest(BaseModel):
    access_type: str
    target_key: str
    unlock_code: str


class CreateMockOrderRequest(BaseModel):
    access_type: str
    target_key: str
    amount: int = 990
    payment_channel: str = "WECHAT"
    max_use_count: int = 1


@router.post("/verify_unlock_code")
def verify_unlock_code(payload: VerifyUnlockCodeRequest) -> dict[str, Any]:
    granted = has_access(payload.access_type, payload.target_key, payload.unlock_code)
    record_usage(
        "/api/payment/verify_unlock_code",
        access_type=payload.access_type,
        target_key=payload.target_key,
        status="OK" if granted else "PAYWALL",
    )
    return {
        "success": granted,
        "code": "OK" if granted else "PAYWALL_REQUIRED",
        "message": "ok" if granted else "unlock code invalid or exhausted",
        "data": {
            "access_type": payload.access_type,
            "target_key": payload.target_key,
            "access_granted": granted,
        },
        "paywall": None
        if granted
        else {
            "required": True,
            "message": "Valid unlock code required.",
            "next_action": "create_mock_order",
        },
        "risk_notice": "Observation only. Not investment advice.",
    }


@router.post("/create_mock_order")
def create_mock_order(payload: CreateMockOrderRequest) -> dict[str, Any]:
    order = create_payment_order(
        payload.access_type,
        payload.target_key,
        payload.amount,
        payload.payment_channel,
    )
    paid = confirm_payment(
        order["order_no"],
        "MOCK-PAID",
        max_use_count=payload.max_use_count,
    )
    record_usage(
        "/api/payment/create_mock_order",
        access_type=payload.access_type,
        target_key=payload.target_key,
        status="OK",
    )
    return {
        "success": True,
        "code": "OK",
        "message": "ok",
        "data": {
            "order": paid["order"],
            "unlock_code": paid["unlock_code"],
        },
        "paywall": None,
        "risk_notice": "Observation only. Not investment advice.",
    }
