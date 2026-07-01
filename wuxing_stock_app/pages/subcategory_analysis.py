"""细分行业付费分析页。"""

from __future__ import annotations

import streamlit as st

from wuxing_stock_app.modules.auth_engine import has_access
from wuxing_stock_app.modules.industry_engine import (
    get_subcategory_profile,
    list_categories,
    list_subcategories,
)


def render_subcategory_analysis() -> None:
    """细分行业需要解锁码。"""
    st.title("细分行业五行分析")
    categories = list_categories()
    category_names = {item["category_name"]: item["category_id"] for item in categories}
    selected_category_name = st.selectbox("选择行业大类", list(category_names.keys()))
    category_id = category_names[selected_category_name]

    previews = list_subcategories(category_id)
    if not previews:
        st.info("当前大类暂无细分行业。")
        return

    subcategory_names = {item["subcategory_name"]: item["subcategory_id"] for item in previews}
    selected_subcategory_name = st.selectbox("选择细分行业", list(subcategory_names.keys()))
    subcategory_id = subcategory_names[selected_subcategory_name]
    target_key = f"subcategory:{subcategory_id}"
    unlock_code = st.text_input("输入解锁码", type="password")
    access_granted = has_access("PAID_SUBCATEGORY_SINGLE", target_key, unlock_code or None)
    profile = get_subcategory_profile(subcategory_id, has_access=access_granted)

    if not access_granted:
        st.warning(profile["unlock_hint"])
        return

    st.success("已解锁")
    col1, col2, col3 = st.columns(3)
    col1.metric("主五行", profile["main_element"])
    col2.metric("副五行", profile["secondary_element"])
    col3.metric("情绪热度", int(profile.get("emotion_heat", 0)))
    st.write(profile["behavior_description"])
    st.write(profile.get("paid_description", ""))
    st.json(profile["element_scores"])
    st.write("风险标签：", "、".join(profile.get("risk_tags", [])))
