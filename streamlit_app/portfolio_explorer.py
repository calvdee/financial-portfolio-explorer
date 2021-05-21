from dataclasses import dataclass, field
import streamlit as st
import pandas as pd
import numpy as np

@dataclass
class PortfolioSummary:
  dollar_cost: float
  dollar_value: float
  dollar_return: float = field(init = False)
  percent_return: float = field(init = False)

  def __post_init__(self):
    self.dollar_return = self.dollar_value - self.dollar_cost
    self.percent_return = self.dollar_value / self.dollar_cost - 1

def build_summary_text(portfolio_summary: PortfolioSummary) -> str:
  invested = portfolio_summary.dollar_cost
  value = portfolio_summary.dollar_value
  dollar_return = portfolio_summary.dollar_return
  percent_return = portfolio_summary.percent_return

  return_type = 'gain' if dollar_return > 0 else 'loss'

  return f"""
  To date, you have invested **${invested:,.0f}** and your current portfolio value is **${value:,.0f}**, a **{return_type}  of {dollar_return:,.0f}** (**{percent_return*100:.1f}%**).
  """

def get_portfolio_summary() -> PortfolioSummary:
  return PortfolioSummary(
    dollar_cost = 7809.18,
    dollar_value = 7785.574905
  )

# Title 
# ===========================================================================================
st.title('Portfolio Explorer')

# Text Summary
# ===========================================================================================
portfolio_summary = get_portfolio_summary()
portfolio_summary_text = build_summary_text(portfolio_summary)

st.markdown(portfolio_summary_text)