"""行业大类免费分析页。"""

from __future__ import annotations

import streamlit as st

from wuxing_stock_app.modules.industry_engine import get_category_profile, list_categories


def render_category_analysis() -> None:
    """展示免费行业大类。"""
    st.title("行业大类五行分析")
    categories = list_categories()
    if not categories:
        st.info("暂无行业大类数据。")
        return

    names = {item["category_name"]: item["category_id"] for item in categories}
    selected_name = st.selectbox("选择行业大类", list(names.keys()))
    profile = get_category_profile(names[selected_name])

    st.success("免费开放")
    col1, col2 = st.columns(2)
    col1.metric("主五行", profile["main_element"])
    col2.metric("副五行", profile["secondary_element"])
    st.write(profile["behavior_description"])
    st.info(profile.get("free_description", ""))
    st.warning(profile.get("paid_hint", "查看细分行业分析，需要付费解锁。"))
    st.json(profile["element_scores"])
