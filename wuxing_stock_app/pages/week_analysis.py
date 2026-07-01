"""周度五行免费分析页。"""

from __future__ import annotations

from datetime import date

import streamlit as st

from wuxing_stock_app.modules.calendar_engine import get_period_element


def render_week_analysis() -> None:
    """周度分析免费展示。"""
    st.title("周度五行分析")
    selected_date = st.date_input("选择周内任意日期", value=date(2026, 7, 1))

    try:
        profile = get_period_element("week", selected_date.isoformat())
    except ValueError as exc:
        st.error(str(exc))
        return

    st.success("免费开放")
    col1, col2, col3 = st.columns(3)
    col1.metric("主五行", str(profile["main_element"]))
    col2.metric("副五行", str(profile["secondary_element"]))
    col3.metric("强度", int(profile["strength_score"]))
    st.write(str(profile["description"]))
