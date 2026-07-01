"""用户记录模块。

负责记录访问、解锁、报告生成等本地行为。
"""

from __future__ import annotations


def record_user_action(action: str, target_key: str, note: str = "") -> dict[str, str]:
    """占位：记录用户行为。"""
    return {"action": action, "target_key": target_key, "note": note}
