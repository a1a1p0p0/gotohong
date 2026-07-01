"""Streamlit 应用入口。"""

from __future__ import annotations

import streamlit as st

from wuxing_stock_app.database import initialize_database
from wuxing_stock_app.pages.category_analysis import render_category_analysis
from wuxing_stock_app.pages.day_analysis import render_day_analysis
from wuxing_stock_app.pages.home import render_home
from wuxing_stock_app.pages.ranking_analysis import render_ranking_analysis
from wuxing_stock_app.pages.subcategory_analysis import render_subcategory_analysis
from wuxing_stock_app.pages.week_analysis import render_week_analysis
from wuxing_stock_app.pages.year_analysis import render_year_analysis


PAGES = {
    "首页": render_home,
    "年度分析": render_year_analysis,
    "周度分析": render_week_analysis,
    "行业大类": render_category_analysis,
    "每日分析": render_day_analysis,
    "细分行业": render_subcategory_analysis,
    "行业方案": render_ranking_analysis,
}


def main() -> None:
    """启动 Streamlit UI。"""
    initialize_database()
    st.set_page_config(page_title="五行股票行业分析软件", layout="wide")
    st.sidebar.title("功能入口")
    page_name = st.sidebar.radio("选择页面", list(PAGES.keys()))
    PAGES[page_name]()


if __name__ == "__main__":
    main()
