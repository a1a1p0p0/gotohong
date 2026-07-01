"""支付模块。

支持记录支付宝、微信真实支付渠道的订单与外部流水号。当前模块不直连支付网关，
只负责本地订单入库、支付确认和解锁码发放。
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from wuxing_stock_app import database
from wuxing_stock_app.modules.auth_engine import ACCESS_TYPES, PAID_ACCESS_TYPES, create_unlock_code


PAYMENT_CHANNELS = {"ALIPAY", "WECHAT"}


def create_payment_order(
    access_type: str,
    target_key: str,
    amount: int,
    payment_channel: str,
    *,
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """创建支付宝或微信支付订单记录。"""
    _validate_paid_access_type(access_type)
    _validate_payment_channel(payment_channel)
    if amount <= 0:
        raise ValueError("amount must be greater than 0")

    database.initialize_database(db_path)
    order_no = f"PAY-{uuid.uuid4().hex[:16].upper()}"
    database.execute(
        """
        INSERT INTO payment_orders
          (order_no, access_type, target_key, amount, payment_channel, status)
        VALUES (?, ?, ?, ?, ?, 'PENDING')
        """,
        (order_no, access_type, target_key, amount, payment_channel),
        db_path,
    )
    order = get_payment_order(order_no, db_path=db_path)
    if order is None:
        raise RuntimeError("failed to create payment order")
    return order


def confirm_payment(
    order_no: str,
    external_trade_no: str,
    *,
    max_use_count: int = 1,
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """确认支付宝或微信支付成功，并创建解锁码。"""
    database.initialize_database(db_path)
    order = get_payment_order(order_no, db_path=db_path)
    if order is None:
        raise ValueError("payment order not found")
    if order["status"] == "PAID":
        unlock = database.fetch_one("SELECT * FROM unlock_codes WHERE order_no = ?", (order_no,), db_path)
        return {"order": order, "unlock_code": unlock}

    database.execute(
        """
        UPDATE payment_orders
        SET status = 'PAID', external_trade_no = ?, paid_at = CURRENT_TIMESTAMP
        WHERE order_no = ?
        """,
        (external_trade_no, order_no),
        db_path,
    )
    updated_order = get_payment_order(order_no, db_path=db_path)
    if updated_order is None:
        raise RuntimeError("payment order disappeared")
    unlock = create_unlock_code(
        updated_order["access_type"],
        updated_order["target_key"],
        max_use_count=max_use_count,
        order_no=order_no,
        db_path=db_path,
    )
    return {"order": updated_order, "unlock_code": unlock}


def get_payment_order(order_no: str, *, db_path: Path | str = database.DB_PATH) -> dict[str, Any] | None:
    """读取支付订单。"""
    database.initialize_database(db_path)
    return database.fetch_one("SELECT * FROM payment_orders WHERE order_no = ?", (order_no,), db_path)


def create_mock_order(
    product_type: str,
    target_key: str,
    amount: int,
    *,
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """兼容旧入口：创建微信待支付订单。"""
    access_type = product_type if product_type in ACCESS_TYPES else "PAID_DAY"
    return create_payment_order(access_type, target_key, amount, "WECHAT", db_path=db_path)


def mark_order_paid(
    order_no: str,
    *,
    external_trade_no: str = "MANUAL-CONFIRMED",
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """兼容旧入口：标记订单已支付。"""
    return confirm_payment(order_no, external_trade_no, db_path=db_path)["order"]


def _validate_payment_channel(payment_channel: str) -> None:
    if payment_channel not in PAYMENT_CHANNELS:
        raise ValueError("payment_channel only supports ALIPAY, WECHAT")


def _validate_paid_access_type(access_type: str) -> None:
    if access_type not in PAID_ACCESS_TYPES:
        raise ValueError("payment order only supports paid access types")
