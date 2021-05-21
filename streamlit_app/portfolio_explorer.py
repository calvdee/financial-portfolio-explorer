from dataclasses import dataclass, field
import streamlit as st
import pandas as pd
import numpy as np

from src import data

def build_summary_text(portfolio_summary: data.PortfolioSummary) -> str:
  invested = portfolio_summary.dollar_cost
  value = portfolio_summary.dollar_value
  dollar_return = portfolio_summary.dollar_return
  percent_return = portfolio_summary.percent_return

  return_type = 'gain' if dollar_return > 0 else 'loss'

  return f"""
  To date, you have invested **${invested:,.0f}** and your current portfolio value is **${value:,.0f}**, a **{return_type}  of {dollar_return:,.0f}** (**{percent_return*100:.1f}%**).
  """

# Data and Preprocessing
# ===========================================================================================
orders_df = data.load_orders('streamlit_app/data/orders.csv')
portfolio_data = data.PortfolioData(orders_df)

# Title 
# ===========================================================================================
st.title('Portfolio Explorer')

# Text Summary
# ===========================================================================================
portfolio_summary = portfolio_data.summarize()
portfolio_summary_text = build_summary_text(portfolio_summary)

st.markdown(portfolio_summary_text)