"""每日五行付费分析页。"""

from __future__ import annotations

from datetime import date

import streamlit as st

from wuxing_stock_app.modules.auth_engine import has_access
from wuxing_stock_app.modules.calendar_engine import get_period_element


def render_day_analysis() -> None:
    """每日分析需要解锁码。"""
    st.title("每日五行分析")
    selected_date = st.date_input("选择日期", value=date(2026, 6, 29))
    target_key = f"day:{selected_date.isoformat()}"
    unlock_code = st.text_input("输入解锁码", type="password")

    if not has_access("PAID_DAY", target_key, unlock_code or None):
        st.warning("每日分析为付费功能，请输入有效解锁码。")
        return

    try:
        profile = get_period_element("day", selected_date.isoformat())
    except ValueError as exc:
        st.error(str(exc))
        return

    st.success("已解锁")
    col1, col2, col3 = st.columns(3)
    col1.metric("主五行", str(profile["main_element"]))
    col2.metric("副五行", str(profile["secondary_element"]))
    col3.metric("强度", int(profile["strength_score"]))
    st.write(str(profile["description"]))
