"""首页。"""

from __future__ import annotations

import streamlit as st


def render_home() -> None:
    """展示功能入口。"""
    st.title("五行股票行业分析软件")
    st.caption("五行不是静态标签，而是行业动能的行为方式。")

    st.subheader("免费功能")
    col1, col2, col3 = st.columns(3)
    col1.info("年度五行分析\n\n免费查看年度动能。")
    col2.info("周度五行分析\n\n免费查看本周动能。")
    col3.info("行业大类分析\n\n免费查看一级行业。")

    st.subheader("付费功能")
    col4, col5, col6 = st.columns(3)
    col4.warning("每日五行分析\n\n需要输入解锁码。")
    col5.warning("细分行业分析\n\n需要输入解锁码。")
    col6.warning("行业方案\n\n免费预览，付费查看完整 TOP 5。")

    st.divider()
    st.write("请从左侧菜单选择功能页面。")
