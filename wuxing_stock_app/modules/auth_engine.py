"""付费权限模块。

负责解锁码生成、使用次数记录和权限判断。所有数据读写统一经过 database.py。
"""

from __future__ import annotations

import secrets
import string
from pathlib import Path
from typing import Any

from wuxing_stock_app import database


FREE_ACCESS_TYPES = {"FREE_YEAR", "FREE_WEEK", "FREE_CATEGORY"}
PAID_ACCESS_TYPES = {
    "PAID_DAY",
    "PAID_SUBCATEGORY_SINGLE",
    "PAID_MONTH_RANKING",
    "PAID_WEEK_RANKING",
    "PAID_DAY_RANKING",
}
ACCESS_TYPES = FREE_ACCESS_TYPES | PAID_ACCESS_TYPES


def create_unlock_code(
    access_type: str,
    target_key: str,
    *,
    max_use_count: int = 1,
    order_no: str | None = None,
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """创建解锁码。"""
    _validate_access_type(access_type)
    if max_use_count < 1:
        raise ValueError("max_use_count must be greater than 0")

    database.initialize_database(db_path)
    code = generate_unlock_code(access_type, target_key)
    database.execute(
        """
        INSERT INTO unlock_codes
          (code, access_type, target_key, max_use_count, used_count, status, order_no)
        VALUES (?, ?, ?, ?, 0, 'ACTIVE', ?)
        """,
        (code, access_type, target_key, max_use_count, order_no),
        db_path,
    )
    created = get_unlock_code(code, db_path=db_path)
    if created is None:
        raise RuntimeError("failed to create unlock code")
    return created


def generate_unlock_code(access_type: str, target_key: str | None = None) -> str:
    """生成本地解锁码。

    target_key 可为空是为了兼容旧调用；新调用应传 access_type 和 target_key。
    """
    if target_key is None:
        target_key = access_type
        access_type = "PAID_DAY"
    safe_type = access_type.replace("_", "")[:8]
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(8))
    return f"WX-{safe_type}-{suffix}"


def use_unlock_code(
    code: str,
    access_type: str,
    target_key: str,
    *,
    db_path: Path | str = database.DB_PATH,
) -> dict[str, Any]:
    """使用一次解锁码，并记录使用次数。"""
    _validate_access_type(access_type)
    database.initialize_database(db_path)
    unlock = get_unlock_code(code, db_path=db_path)
    if unlock is None:
        raise ValueError("unlock code not found")
    if unlock["status"] != "ACTIVE":
        raise ValueError("unlock code is not active")
    if unlock["access_type"] != access_type or unlock["target_key"] != target_key:
        raise ValueError("unlock code target mismatch")
    if int(unlock["used_count"]) >= int(unlock["max_use_count"]):
        raise ValueError("unlock code use count exceeded")

    database.execute(
        "UPDATE unlock_codes SET used_count = used_count + 1 WHERE code = ?",
        (code,),
        db_path,
    )
    updated = get_unlock_code(code, db_path=db_path)
    if updated is None:
        raise RuntimeError("unlock code disappeared")
    if int(updated["used_count"]) >= int(updated["max_use_count"]):
        database.execute("UPDATE unlock_codes SET status = 'USED' WHERE code = ?", (code,), db_path)
        updated = get_unlock_code(code, db_path=db_path)
        if updated is None:
            raise RuntimeError("unlock code disappeared")

    database.execute(
        """
        INSERT INTO access_usage_logs (access_type, target_key, unlock_code, action, note)
        VALUES (?, ?, ?, 'UNLOCK', 'unlock code used')
        """,
        (access_type, target_key, code),
        db_path,
    )
    return updated


def has_access(
    access_type: str,
    target_key: str,
    unlock_code: str | None = None,
    *,
    db_path: Path | str = database.DB_PATH,
) -> bool:
    """判断是否有访问权限。免费权限直接放行，付费权限检查解锁码记录。"""
    _validate_access_type(access_type)
    if access_type in FREE_ACCESS_TYPES:
        return True
    if not unlock_code:
        return False

    database.initialize_database(db_path)
    unlock = get_unlock_code(unlock_code, db_path=db_path)
    if unlock is None:
        return False
    return (
        unlock["access_type"] == access_type
        and unlock["target_key"] == target_key
        and unlock["status"] == "ACTIVE"
        and int(unlock["used_count"]) < int(unlock["max_use_count"])
    )


def get_unlock_code(code: str, *, db_path: Path | str = database.DB_PATH) -> dict[str, Any] | None:
    """读取解锁码。"""
    database.initialize_database(db_path)
    return database.fetch_one("SELECT * FROM unlock_codes WHERE code = ?", (code,), db_path)


def _validate_access_type(access_type: str) -> None:
    if access_type not in ACCESS_TYPES:
        raise ValueError(f"unsupported access_type: {access_type}")
