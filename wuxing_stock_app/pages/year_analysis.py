"""年度五行免费分析页。"""

from __future__ import annotations

from datetime import date

import streamlit as st

from wuxing_stock_app.modules.calendar_engine import get_period_element


def render_year_analysis() -> None:
    """年度分析免费展示。"""
    st.title("年度五行分析")
    selected_year = st.number_input("选择年份", min_value=1900, max_value=2100, value=2026, step=1)
    query_date = date(int(selected_year), 6, 29).isoformat()

    try:
        profile = get_period_element("year", query_date)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.success("免费开放")
    _render_time_profile(profile)


def _render_time_profile(profile: dict[str, object]) -> None:
    st.metric("主五行", str(profile["main_element"]))
    st.metric("副五行", str(profile["secondary_element"]))
    st.metric("强度", int(profile["strength_score"]))
    st.write(str(profile["description"]))
