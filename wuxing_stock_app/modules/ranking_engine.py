"""行业筛选模块。

负责根据时间五行、行业五行动能和规则关系，计算最有利行业与最平衡行业。
本模块只做业务计算，不处理 UI。
"""

from __future__ import annotations

from typing import Any

from wuxing_stock_app import database
from wuxing_stock_app.modules.calendar_engine import get_period_element
from wuxing_stock_app.modules.rule_engine import CONTROLS, GENERATES, calculate_all_relations


SUPPORTED_PERIOD_TYPES = {"month", "week", "day"}
SUPPORTED_RANKING_TYPES = {"favorable", "balanced"}


def rank_industries(period_type: str, date_text: str, ranking_type: str) -> list[dict[str, Any]]:
    """按时间维度输出 TOP 5 行业。

    period_type 支持：month、week、day。
    ranking_type 支持：favorable、balanced。
    """
    if period_type not in SUPPORTED_PERIOD_TYPES:
        raise ValueError("period_type only supports month, week, day")
    if ranking_type not in SUPPORTED_RANKING_TYPES:
        raise ValueError("ranking_type only supports favorable, balanced")

    time_profile = get_period_element(period_type, date_text)
    industries = _list_ranking_profiles()

    ranked = []
    for industry in industries:
        score_result = (
            _calculate_favorable_score(time_profile, industry)
            if ranking_type == "favorable"
            else _calculate_balanced_score(time_profile, industry)
        )
        ranked.append(
            {
                "rank": 0,
                "industry_id": industry["subcategory_id"],
                "industry_name": industry["subcategory_name"],
                "main_element": industry["main_element"],
                "secondary_element": industry["secondary_element"],
                "score": score_result["score"],
                "reason": score_result["reason"],
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["industry_id"]))
    top5 = ranked[:5]
    for index, item in enumerate(top5, start=1):
        item["rank"] = index
    return top5


def _calculate_favorable_score(time_profile: dict[str, Any], industry: dict[str, Any]) -> dict[str, Any]:
    """最有利行业：强调五行顺势、启动、承接和放大。"""
    time_element = time_profile["main_element"]
    main_element = industry["main_element"]
    secondary_element = industry["secondary_element"]
    element_scores = industry["element_scores"]

    relations = calculate_all_relations(
        time_element,
        main_element,
        secondary_element,
        time_strength=int(time_profile["strength_score"]),
        industry_main_strength=int(element_scores[main_element]),
        industry_secondary_strength=int(element_scores[secondary_element]),
    )

    details: list[str] = []
    score = 0

    score += relations["main"]["score"]
    details.append(relations["main"]["description"])

    secondary_score = round(relations["secondary"]["score"] * 0.5)
    score += secondary_score
    details.append(f"副五行关系折算 {secondary_score} 分。")

    if max(element_scores.values()) > 45:
        score -= 10
        details.append("行业五行过旺，顺势中需要防止单边过亢。")

    return {
        "score": score,
        "reason": _build_reason("favorable", industry["subcategory_name"], details),
    }


def _calculate_balanced_score(time_profile: dict[str, Any], industry: dict[str, Any]) -> dict[str, Any]:
    """最平衡行业：强调结构、承接、制约、不过亢。"""
    time_element = time_profile["main_element"]
    main_element = industry["main_element"]
    secondary_element = industry["secondary_element"]
    element_scores = industry["element_scores"]

    relations = calculate_all_relations(
        time_element,
        main_element,
        secondary_element,
        time_strength=int(time_profile["strength_score"]),
        industry_main_strength=int(element_scores[main_element]),
        industry_secondary_strength=int(element_scores[secondary_element]),
    )

    details: list[str] = []
    score = 0

    if abs(element_scores[main_element] - element_scores[secondary_element]) <= 15:
        score += 20
        details.append("主五行与副五行差距较小，结构不偏单边。")

    if _active_element_count(element_scores) >= 3:
        score += 15
        details.append("至少三种五行参与，结构层次更完整。")

    relation_types = {relations["main"]["relation_type"], relations["secondary"]["relation_type"]}
    if relation_types & {"generating", "transforming"}:
        score += 15
        details.append("时间五行与行业五行存在承接或转化关系。")

    if relation_types & {"controlling", "regulating"}:
        score += 10
        details.append("结构中存在适度制约，有利于防止过亢。")

    if max(element_scores.values()) > 60:
        score -= 25
        details.append("单一五行占比过高，平衡性下降。")

    if relations["main"]["relation_type"] == "over_controlling":
        score -= 30
        details.append("时间五行强克行业主五行，结构稳定性受压。")

    if _has_supporting_element(element_scores, main_element):
        score += 15
        details.append("结构中有承接元素。")

    if _has_restraining_element(element_scores, main_element):
        score += 15
        details.append("结构中有制约元素。")

    return {
        "score": score,
        "reason": _build_reason("balanced", industry["subcategory_name"], details),
    }


def _active_element_count(element_scores: dict[str, int]) -> int:
    return sum(1 for score in element_scores.values() if int(score) >= 10)


def _list_ranking_profiles() -> list[dict[str, Any]]:
    database.initialize_database()
    rows = database.fetch_all(
        """
        SELECT board_code, board_name, board_type, main_element, secondary_element,
               wood_score, fire_score, earth_score, metal_score, water_score, reason
        FROM astock_board_wuxing_profiles
        WHERE need_review = 'false'
        ORDER BY board_type ASC, board_code ASC
        """
    )
    return [
        {
            "subcategory_id": row["board_code"],
            "subcategory_name": row["board_name"],
            "main_element": row["main_element"],
            "secondary_element": row["secondary_element"],
            "element_scores": {
                "wood": int(row["wood_score"]),
                "fire": int(row["fire_score"]),
                "earth": int(row["earth_score"]),
                "metal": int(row["metal_score"]),
                "water": int(row["water_score"]),
            },
            "source_reason": row["reason"],
        }
        for row in rows
    ]


def _has_supporting_element(element_scores: dict[str, int], main_element: str) -> bool:
    supporting_element = next(element for element, generated in GENERATES.items() if generated == main_element)
    return int(element_scores.get(supporting_element, 0)) >= 15


def _has_restraining_element(element_scores: dict[str, int], main_element: str) -> bool:
    restraining_element = next(element for element, controlled in CONTROLS.items() if controlled == main_element)
    return int(element_scores.get(restraining_element, 0)) >= 10


def _build_reason(ranking_type: str, industry_name: str, details: list[str]) -> str:
    focus = (
        "最有利行业强调五行顺势、启动、承接和放大"
        if ranking_type == "favorable"
        else "最平衡行业强调结构、承接、制约、不过亢"
    )
    reason_detail = "；".join(details[:3]) if details else "暂无显著评分项"
    return f"{industry_name}入选依据：{focus}。{reason_detail}"
