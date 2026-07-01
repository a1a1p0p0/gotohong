"""五行规则判断模块。

五行不是静态标签，而是行业动能的行为方式。本模块只负责规则判断，
不读写数据库，也不处理 UI。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
RULES_PATH = BASE_DIR / "data" / "wuxing_rules.json"

ELEMENTS = ("wood", "fire", "earth", "metal", "water")

GENERATES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}

CONTROLS = {
    "wood": "earth",
    "earth": "water",
    "water": "fire",
    "fire": "metal",
    "metal": "wood",
}


def load_wuxing_rules(path: str | Path = RULES_PATH) -> dict[str, Any]:
    """读取五行规则配置。"""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def get_element_definition(element: str) -> dict[str, Any]:
    """获取单个五行动能定义。"""
    _validate_element(element)
    return load_wuxing_rules()["elements"][element]


def calculate_relation(
    time_element: str,
    industry_element: str,
    *,
    time_strength: int = 50,
    industry_strength: int = 50,
    secondary_element: str | None = None,
) -> dict[str, Any]:
    """判断时间五行和行业五行关系。

    返回字段固定包含：
    - relation_type
    - score
    - description

    强度用于区分相克、相乘、相侮。默认强度为 50，表示普通关系。
    """
    _validate_element(time_element)
    _validate_element(industry_element)
    if secondary_element is not None:
        _validate_element(secondary_element)

    time_strength = _normalize_strength(time_strength)
    industry_strength = _normalize_strength(industry_strength)

    relation_type = _resolve_relation_type(
        time_element=time_element,
        industry_element=industry_element,
        time_strength=time_strength,
        industry_strength=industry_strength,
        secondary_element=secondary_element,
    )
    rule = load_wuxing_rules()["relations"][relation_type]

    return {
        "relation_type": relation_type,
        "score": int(rule["score"]),
        "description": _format_description(
            template=rule["description"],
            time_element=time_element,
            industry_element=industry_element,
            secondary_element=secondary_element,
        ),
    }


def calculate_all_relations(
    time_element: str,
    industry_main_element: str,
    industry_secondary_element: str,
    *,
    time_strength: int = 50,
    industry_main_strength: int = 50,
    industry_secondary_strength: int = 50,
) -> dict[str, dict[str, Any]]:
    """同时判断时间五行与行业主五行、副五行的关系。"""
    return {
        "main": calculate_relation(
            time_element,
            industry_main_element,
            time_strength=time_strength,
            industry_strength=industry_main_strength,
        ),
        "secondary": calculate_relation(
            time_element,
            industry_secondary_element,
            time_strength=time_strength,
            industry_strength=industry_secondary_strength,
        ),
    }


def _resolve_relation_type(
    *,
    time_element: str,
    industry_element: str,
    time_strength: int,
    industry_strength: int,
    secondary_element: str | None,
) -> str:
    if time_element == industry_element:
        return "transforming"

    if secondary_element and GENERATES[time_element] == industry_element and GENERATES[industry_element] == secondary_element:
        return "transforming"

    if GENERATES[time_element] == industry_element:
        return "generating"

    if GENERATES[industry_element] == time_element:
        return "consuming"

    if CONTROLS[time_element] == industry_element:
        if time_strength - industry_strength >= 30:
            return "over_controlling"
        if industry_strength - time_strength >= 30:
            return "reverse_controlling"
        return "controlling"

    if CONTROLS[industry_element] == time_element:
        return "regulating"

    return "neutral"


def _format_description(
    *,
    template: str,
    time_element: str,
    industry_element: str,
    secondary_element: str | None,
) -> str:
    labels = load_wuxing_rules()["element_labels"]
    return template.format(
        time_element=labels[time_element],
        industry_element=labels[industry_element],
        secondary_element=labels.get(secondary_element or "", ""),
    )


def _normalize_strength(value: int) -> int:
    return max(0, min(100, int(value)))


def _validate_element(element: str) -> None:
    if element not in ELEMENTS:
        raise ValueError(f"unsupported element: {element}")
