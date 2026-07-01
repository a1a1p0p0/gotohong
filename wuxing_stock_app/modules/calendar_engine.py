"""时间五行模块。

从本地 CSV 读取日期、天干、地支，并按天干地支映射五行。
分析引擎默认使用 lichun_year_ganzhi 作为年干支，月干支采用节气月。
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
CALENDAR_PATH = BASE_DIR / "data" / "calendar_ganzhi.csv"

STEM_ELEMENTS = {
    "甲": "wood",
    "乙": "wood",
    "丙": "fire",
    "丁": "fire",
    "戊": "earth",
    "己": "earth",
    "庚": "metal",
    "辛": "metal",
    "壬": "water",
    "癸": "water",
}

BRANCH_ELEMENTS = {
    "寅": "wood",
    "卯": "wood",
    "巳": "fire",
    "午": "fire",
    "辰": "earth",
    "戌": "earth",
    "丑": "earth",
    "未": "earth",
    "申": "metal",
    "酉": "metal",
    "亥": "water",
    "子": "water",
}

ELEMENT_LABELS = {
    "wood": "木",
    "fire": "火",
    "earth": "土",
    "metal": "金",
    "water": "水",
}


def load_calendar_rows(path: str | Path = CALENDAR_PATH) -> list[dict[str, str]]:
    """读取干支日历 CSV。"""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def get_period_element(period_type: str, date_text: str) -> dict[str, Any]:
    """获取指定时间维度的主五行、副五行和强度。"""
    if period_type not in {"year", "month", "week", "day"}:
        raise ValueError("period_type only supports year, month, week, day")

    target_date = _parse_date(date_text)
    rows = load_calendar_rows()
    row_by_date = {row["date"]: row for row in rows}

    if period_type == "week":
        elements = _week_elements(target_date, row_by_date)
    else:
        row = _get_row(target_date, row_by_date)
        elements = _period_elements_from_row(period_type, row)

    main_element, secondary_element, strength_score = _summarize_elements(elements)

    return {
        "period_type": period_type,
        "date": target_date.isoformat(),
        "main_element": main_element,
        "secondary_element": secondary_element,
        "strength_score": strength_score,
        "description": _build_description(period_type, main_element, secondary_element, strength_score),
    }


def stem_to_element(stem: str) -> str:
    """天干映射五行。"""
    try:
        return STEM_ELEMENTS[stem]
    except KeyError as exc:
        raise ValueError(f"unsupported heavenly stem: {stem}") from exc


def branch_to_element(branch: str) -> str:
    """地支映射五行。"""
    try:
        return BRANCH_ELEMENTS[branch]
    except KeyError as exc:
        raise ValueError(f"unsupported earthly branch: {branch}") from exc


def _period_elements_from_row(period_type: str, row: dict[str, str]) -> list[str]:
    if period_type == "year":
        gan_key, zhi_key = "year_gan", "year_zhi"
    elif period_type == "month":
        gan_key, zhi_key = "month_gan", "month_zhi"
    else:
        gan_key, zhi_key = "day_gan", "day_zhi"
    return [stem_to_element(row[gan_key]), branch_to_element(row[zhi_key])]


def _week_elements(target_date: date, row_by_date: dict[str, dict[str, str]]) -> list[str]:
    week_start = target_date - timedelta(days=target_date.weekday())
    elements: list[str] = []
    for offset in range(7):
        current_date = week_start + timedelta(days=offset)
        row = _get_row(current_date, row_by_date)
        elements.extend(_period_elements_from_row("day", row))
    return elements


def _summarize_elements(elements: list[str]) -> tuple[str, str, int]:
    counts = Counter(elements)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    main_element = ranked[0][0]
    secondary_element = ranked[1][0] if len(ranked) > 1 else ranked[0][0]
    strength_score = round(ranked[0][1] / len(elements) * 100)
    return main_element, secondary_element, strength_score


def _build_description(
    period_type: str,
    main_element: str,
    secondary_element: str,
    strength_score: int,
) -> str:
    period_label = {
        "year": "年度",
        "month": "月度",
        "week": "周度",
        "day": "日度",
    }[period_type]
    return (
        f"{period_label}主五行为{ELEMENT_LABELS[main_element]}，"
        f"副五行为{ELEMENT_LABELS[secondary_element]}，"
        f"主五行强度为{strength_score}。"
    )


def _get_row(target_date: date, row_by_date: dict[str, dict[str, str]]) -> dict[str, str]:
    key = target_date.isoformat()
    try:
        return row_by_date[key]
    except KeyError as exc:
        raise ValueError(f"date not found in calendar_ganzhi.csv: {key}") from exc


def _parse_date(date_text: str) -> date:
    return datetime.strptime(date_text, "%Y-%m-%d").date()
