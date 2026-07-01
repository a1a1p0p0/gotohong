from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


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

ELEMENT_LABELS = {
    "wood": "木",
    "fire": "火",
    "earth": "土",
    "metal": "金",
    "water": "水",
}

DEFAULT_PROFILE_PATH = Path(__file__).resolve().parents[1] / "data" / "industry_profiles.json"


def calculate_element_relation(
    time_element: str,
    industry_main_element: str,
    industry_secondary_element: str,
) -> dict[str, Any]:
    """判断时间五行与行业主、副五行的相生、相克、相耗、相制关系。"""
    _validate_element(time_element)
    _validate_element(industry_main_element)
    _validate_element(industry_secondary_element)

    main_relation = _pair_relation(time_element, industry_main_element)
    secondary_relation = _pair_relation(time_element, industry_secondary_element)
    relation_types = {main_relation["type"], secondary_relation["type"]}

    return {
        "time_element": time_element,
        "industry_main_element": industry_main_element,
        "industry_secondary_element": industry_secondary_element,
        "main_relation": main_relation,
        "secondary_relation": secondary_relation,
        "is_generating": "time_generates_industry" in relation_types,
        "is_controlling": "time_controls_industry" in relation_types,
        "is_consuming": "industry_generates_time" in relation_types,
        "is_regulating": _has_regulating_relation(main_relation, secondary_relation),
        "summary": _relation_summary(time_element, industry_main_element, industry_secondary_element),
    }


def calculate_favorable_score(
    time_element_profile: dict[str, Any],
    industry_profile: dict[str, Any],
) -> dict[str, Any]:
    """计算某个时间维度下最有利行业分数。"""
    time_element = time_element_profile["main_element"]
    main_element = industry_profile["main_element"]
    secondary_element = industry_profile["secondary_element"]
    element_scores = _element_scores(industry_profile)
    emotion_heat = int(industry_profile.get("emotion_heat", 50))

    _validate_element(time_element)
    _validate_element(main_element)
    _validate_element(secondary_element)

    score = 0
    details: list[dict[str, Any]] = []

    score = _add_if(score, details, GENERATES[time_element] == main_element, 30, "时间五行生行业主五行")
    score = _add_if(score, details, time_element == main_element, 20, "时间五行同行业主五行")
    score = _add_if(score, details, GENERATES[time_element] == secondary_element, 15, "时间五行生行业副五行")
    score = _add_if(score, details, CONTROLS[main_element] == time_element, 8, "行业主五行克时间五行")
    score = _add_if(score, details, GENERATES[main_element] == time_element, -10, "行业主五行生时间五行")
    score = _add_if(score, details, CONTROLS[time_element] == main_element, -30, "时间五行克行业主五行")
    score = _add_if(score, details, CONTROLS[time_element] == secondary_element, -15, "时间五行克行业副五行")
    score = _add_if(score, details, _is_overpowered(element_scores), -10, "行业五行过旺")
    score = _add_if(score, details, 70 <= emotion_heat <= 85, 10, "当前情绪热度高")
    score = _add_if(score, details, emotion_heat > 85, -10, "当前情绪热度过高")

    return {
        "score": score,
        "ranking_type": "favorable",
        "relation": calculate_element_relation(time_element, main_element, secondary_element),
        "details": details,
        "reason": _build_reason("favorable", time_element, industry_profile, details),
    }


def calculate_balance_score(
    time_element_profile: dict[str, Any],
    industry_profile: dict[str, Any],
) -> dict[str, Any]:
    """计算某个时间维度下最平衡行业分数。"""
    time_element = time_element_profile["main_element"]
    main_element = industry_profile["main_element"]
    secondary_element = industry_profile["secondary_element"]
    element_scores = _element_scores(industry_profile)
    emotion_heat = int(industry_profile.get("emotion_heat", 50))

    _validate_element(time_element)
    _validate_element(main_element)
    _validate_element(secondary_element)

    score = 0
    details: list[dict[str, Any]] = []

    score = _add_if(score, details, _main_secondary_gap(element_scores, main_element, secondary_element) <= 12, 20, "主五行和副五行差距小")
    score = _add_if(score, details, _active_element_count(element_scores) >= 3, 15, "行业五行中至少有三种元素参与")
    score = _add_if(score, details, GENERATES[time_element] in (main_element, secondary_element), 15, "时间五行与行业五行形成相生")
    score = _add_if(score, details, CONTROLS[time_element] == secondary_element or CONTROLS[main_element] == time_element, 10, "时间五行与行业五行形成适度相克")
    score = _add_if(score, details, max(element_scores.values()) > 60, -25, "单一五行占比超过 60%")
    score = _add_if(score, details, CONTROLS[time_element] == main_element, -30, "时间五行强克行业主五行")
    score = _add_if(score, details, emotion_heat > 85, -15, "情绪热度过高")
    score = _add_if(score, details, emotion_heat < 35, -10, "情绪热度过低")
    score = _add_if(score, details, _has_supporting_element(element_scores, main_element), 15, "结构中有承接元素")
    score = _add_if(score, details, _has_restraining_element(element_scores, main_element), 15, "结构中有制约元素")

    return {
        "score": score,
        "ranking_type": "balanced",
        "relation": calculate_element_relation(time_element, main_element, secondary_element),
        "details": details,
        "reason": _build_reason("balanced", time_element, industry_profile, details),
    }


def rank_industries_by_period(
    period_type: str,
    date: str | date | datetime,
    ranking_type: str,
    profile_path: str | Path = DEFAULT_PROFILE_PATH,
) -> list[dict[str, Any]]:
    """按月、周、日输出最有利或最平衡 TOP 5 细分行业。"""
    if period_type not in {"month", "week", "day"}:
        raise ValueError("period_type only supports month, week, day")
    if ranking_type not in {"favorable", "balanced"}:
        raise ValueError("ranking_type only supports favorable, balanced")

    target_date = _parse_date(date)
    time_profile = build_time_element_profile(period_type, target_date)
    industries = load_industry_profiles(profile_path)["subcategories"]

    calculator = calculate_favorable_score if ranking_type == "favorable" else calculate_balance_score
    ranked = []
    for industry in industries:
        result = calculator(time_profile, industry)
        ranked.append(
            {
                "rank": 0,
                "score": result["score"],
                "period_type": period_type,
                "period_key": time_profile["period_key"],
                "ranking_type": ranking_type,
                "subcategory_id": industry["subcategory_id"],
                "category_id": industry["category_id"],
                "subcategory_name": industry["subcategory_name"],
                "main_element": industry["main_element"],
                "secondary_element": industry["secondary_element"],
                "emotion_heat": industry.get("emotion_heat", 50),
                "reason": result["reason"],
                "score_details": result["details"],
                "relation": result["relation"],
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["subcategory_id"]))
    top5 = ranked[:5]
    for index, item in enumerate(top5, start=1):
        item["rank"] = index
    return top5


def build_time_element_profile(period_type: str, target_date: date) -> dict[str, Any]:
    """构造本地可用的时间五行。后续可替换为 SQLite 中的 period_element_analysis。"""
    if period_type == "month":
        index = target_date.month - 1
        period_key = target_date.strftime("%Y-%m")
    elif period_type == "week":
        index = target_date.isocalendar().week - 1
        period_key = f"{target_date.isocalendar().year}-W{target_date.isocalendar().week:02d}"
    elif period_type == "day":
        index = target_date.toordinal()
        period_key = target_date.isoformat()
    else:
        raise ValueError("period_type only supports month, week, day")

    main_element = ELEMENTS[index % len(ELEMENTS)]
    secondary_element = ELEMENTS[(index + 1) % len(ELEMENTS)]
    return {
        "period_type": period_type,
        "period_key": period_key,
        "main_element": main_element,
        "secondary_element": secondary_element,
        "energy_strength": 70,
        "emotion_heat": 65,
    }


def load_industry_profiles(profile_path: str | Path = DEFAULT_PROFILE_PATH) -> dict[str, Any]:
    with Path(profile_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _pair_relation(time_element: str, industry_element: str) -> dict[str, str]:
    if time_element == industry_element:
        relation_type = "same"
        label = "同气"
        description = "时间五行与行业五行同频，容易形成共振。"
    elif GENERATES[time_element] == industry_element:
        relation_type = "time_generates_industry"
        label = "相生"
        description = "时间五行生行业五行，行业更容易获得动能滋养。"
    elif GENERATES[industry_element] == time_element:
        relation_type = "industry_generates_time"
        label = "相耗"
        description = "行业五行生时间五行，行业处于输出和消耗状态。"
    elif CONTROLS[time_element] == industry_element:
        relation_type = "time_controls_industry"
        label = "相克"
        description = "时间五行克行业五行，行业动能容易受到压制。"
    elif CONTROLS[industry_element] == time_element:
        relation_type = "industry_controls_time"
        label = "相制"
        description = "行业五行克时间五行，行业具备调用和约束当前环境的能力。"
    else:
        relation_type = "neutral"
        label = "平"
        description = "时间五行与行业五行关系较弱。"

    return {
        "element": industry_element,
        "type": relation_type,
        "label": label,
        "description": description,
    }


def _has_regulating_relation(main_relation: dict[str, str], secondary_relation: dict[str, str]) -> bool:
    relation_types = {main_relation["type"], secondary_relation["type"]}
    return bool({"time_controls_industry", "industry_controls_time"} & relation_types) and bool(
        {"time_generates_industry", "same", "industry_generates_time"} & relation_types
    )


def _relation_summary(time_element: str, main_element: str, secondary_element: str) -> str:
    return (
        f"时间五行{ELEMENT_LABELS[time_element]}与行业主五行{ELEMENT_LABELS[main_element]}、"
        f"副五行{ELEMENT_LABELS[secondary_element]}形成复合关系。"
    )


def _element_scores(industry_profile: dict[str, Any]) -> dict[str, int]:
    scores = industry_profile.get("element_scores", {})
    return {element: int(scores.get(element, 0)) for element in ELEMENTS}


def _is_overpowered(element_scores: dict[str, int]) -> bool:
    return max(element_scores.values(), default=0) > 45


def _main_secondary_gap(element_scores: dict[str, int], main_element: str, secondary_element: str) -> int:
    return abs(element_scores.get(main_element, 0) - element_scores.get(secondary_element, 0))


def _active_element_count(element_scores: dict[str, int]) -> int:
    return sum(1 for score in element_scores.values() if score >= 10)


def _has_supporting_element(element_scores: dict[str, int], main_element: str) -> bool:
    supporting_element = next(element for element, generated in GENERATES.items() if generated == main_element)
    return element_scores.get(supporting_element, 0) >= 15


def _has_restraining_element(element_scores: dict[str, int], main_element: str) -> bool:
    restraining_element = next(element for element, controlled in CONTROLS.items() if controlled == main_element)
    return element_scores.get(restraining_element, 0) >= 10


def _add_if(
    score: int,
    details: list[dict[str, Any]],
    condition: bool,
    points: int,
    reason: str,
) -> int:
    if condition:
        details.append({"reason": reason, "points": points})
        return score + points
    return score


def _build_reason(
    ranking_type: str,
    time_element: str,
    industry_profile: dict[str, Any],
    details: list[dict[str, Any]],
) -> str:
    industry_name = industry_profile.get("subcategory_name") or industry_profile.get("category_name") or "该行业"
    reasons = "、".join(detail["reason"] for detail in details[:3]) or "未命中显著加分项"
    if ranking_type == "favorable":
        focus = "顺势、情绪、启动和放大"
    else:
        focus = "结构、承接、稳定和可持续"
    return f"{industry_name}在{ELEMENT_LABELS[time_element]}时间下主要体现{focus}，关键依据为：{reasons}。"


def _parse_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _validate_element(element: str) -> None:
    if element not in ELEMENTS:
        raise ValueError(f"unsupported element: {element}")
