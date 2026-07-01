"""行业方案榜单页。"""

from __future__ import annotations

from datetime import date

import streamlit as st

from wuxing_stock_app.modules.auth_engine import has_access
from wuxing_stock_app.modules.ranking_engine import rank_industries


ACCESS_TYPE_BY_PERIOD = {
    "month": "PAID_MONTH_RANKING",
    "week": "PAID_WEEK_RANKING",
    "day": "PAID_DAY_RANKING",
}


def render_ranking_analysis() -> None:
    """行业方案支持免费预览和付费完整报告。"""
    st.title("行业方案")
    period_label = st.radio("时间维度", ["月", "周", "日"], horizontal=True)
    ranking_label = st.radio("方案类型", ["最有利", "最平衡"], horizontal=True)
    selected_date = st.date_input("选择日期", value=date(2026, 7, 1))

    period_type = {"月": "month", "周": "week", "日": "day"}[period_label]
    ranking_type = {"最有利": "favorable", "最平衡": "balanced"}[ranking_label]
    target_key = f"ranking:{period_type}:{ranking_type}:{selected_date.isoformat()}"

    unlock_code = st.text_input("输入榜单解锁码，可查看完整 TOP 5", type="password")
    access_granted = has_access(ACCESS_TYPE_BY_PERIOD[period_type], target_key, unlock_code or None)

    try:
        ranking = rank_industries(period_type, selected_date.isoformat(), ranking_type)
    except ValueError as exc:
        st.error(str(exc))
        return

    visible_ranking = ranking if access_granted else ranking[:1]
    st.info("免费预览第 1 名；输入有效解锁码后查看完整 TOP 5。")
    if access_granted:
        st.success("已解锁完整报告")

    for item in visible_ranking:
        st.subheader(f"#{item['rank']} {item['industry_name']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("主五行", item["main_element"])
        col2.metric("副五行", item["secondary_element"])
        col3.metric("分数", int(item["score"]))
        st.write(item["reason"])
        st.divider()
