"""行业数据库模块。

负责读取一级行业大类、二级细分行业和行业五行动能资料。
行业大类免费开放；细分行业需要权限判断后才返回完整资料。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
CATEGORIES_PATH = BASE_DIR / "data" / "industry_categories.json"
SUBCATEGORIES_PATH = BASE_DIR / "data" / "industry_subcategories.json"

ELEMENT_KEYS = ("wood", "fire", "earth", "metal", "water")


def list_categories() -> list[dict[str, Any]]:
    """返回全部免费行业大类。"""
    return [_normalize_category(item) for item in _load_json_list(CATEGORIES_PATH)]


def get_category_profile(category_id: str) -> dict[str, Any]:
    """读取单个免费行业大类完整资料。"""
    for category in list_categories():
        if category["category_id"] == category_id:
            return category
    raise ValueError(f"category not found: {category_id}")


def list_subcategories(
    category_id: str | None = None,
    *,
    has_access: bool = False,
    unlocked_subcategory_ids: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """返回细分行业列表。

    未授权时返回锁定预览；授权时返回完整细分行业资料。
    """
    unlocked_ids = set(unlocked_subcategory_ids or [])
    result = []
    for item in _load_json_list(SUBCATEGORIES_PATH):
        if category_id is not None and item["category_id"] != category_id:
            continue
        access_granted = has_access or item["subcategory_id"] in unlocked_ids
        result.append(_normalize_subcategory(item, access_granted=access_granted))
    return result


def get_subcategory_profile(
    subcategory_id: str,
    *,
    has_access: bool = False,
    unlocked_subcategory_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """读取单个细分行业资料。

    细分行业默认需要权限。未授权时只返回锁定预览，不返回完整五行分数和风险标签。
    """
    unlocked_ids = set(unlocked_subcategory_ids or [])
    for item in _load_json_list(SUBCATEGORIES_PATH):
        if item["subcategory_id"] == subcategory_id:
            access_granted = has_access or subcategory_id in unlocked_ids
            return _normalize_subcategory(item, access_granted=access_granted)
    raise ValueError(f"subcategory not found: {subcategory_id}")


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"expected list json: {path}")
    return data


def _normalize_category(item: dict[str, Any]) -> dict[str, Any]:
    _validate_industry_profile(item, id_key="category_id")
    return {
        **item,
        "is_free": True,
        "paid_required": False,
        "access_granted": True,
        "risk_tags": list(item.get("risk_tags", [])),
    }


def _normalize_subcategory(item: dict[str, Any], *, access_granted: bool) -> dict[str, Any]:
    if not access_granted:
        return {
            "subcategory_id": item["subcategory_id"],
            "category_id": item["category_id"],
            "subcategory_name": item["subcategory_name"],
            "paid_required": True,
            "access_granted": False,
            "locked": True,
            "unlock_hint": "细分行业需要付费解锁后查看完整五行动能资料。",
        }

    _validate_industry_profile(item, id_key="subcategory_id")
    return {
        **item,
        "paid_required": True,
        "access_granted": True,
        "locked": False,
        "risk_tags": list(item.get("risk_tags", [])),
    }


def _validate_industry_profile(item: dict[str, Any], *, id_key: str) -> None:
    required_keys = {
        id_key,
        "main_element",
        "secondary_element",
        "element_scores",
        "behavior_description",
    }
    missing_keys = sorted(required_keys - set(item))
    if missing_keys:
        raise ValueError(f"industry profile missing keys: {missing_keys}")

    scores = item["element_scores"]
    if not isinstance(scores, dict):
        raise ValueError("element_scores must be a dict")

    missing_elements = sorted(set(ELEMENT_KEYS) - set(scores))
    if missing_elements:
        raise ValueError(f"element_scores missing elements: {missing_elements}")
