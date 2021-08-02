import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

# from src.charts import plot_portfolio_value, plot_asset_value
from src import data
from src.portfolio import (
  PortfolioSummary,
  PortfolioData
)
from src.returns import PortfolioReturns
import plotly.graph_objects as go
import plotly.express as px
from src.portfolio import PortfolioData

# Charts
def plot_portfolio_value(portfolio_data: PortfolioData):
  snapshot = portfolio_data.portfolio_snapshot

  fig = go.Figure()

  fig.add_trace(go.Scatter(
    x = snapshot.index,
    y = snapshot['portfolio_cost_usd'],
    mode = 'lines',
    name = 'Portfolio Cost'
  ))

  fig.add_trace(go.Scatter(
    x = snapshot.index,
    y = snapshot['portfolio_value_usd'],
    mode = 'lines',
    name = 'Portfolio Value'
  ))

  fig.update_layout(
    # plot_bgcolor = '#ffffff',
    margin = dict(l=0, r=0, t=0, b=0),
    height = 250
  )

  return fig

def plot_asset_value(portfolio_data: PortfolioData):
  snapshot = (
    portfolio_data
      .asset_snapshot
      .reset_index()
      .melt(
        id_vars = ['snapshot_date', 'asset']
      )
  )

  fig = px.line(
    snapshot, 
    x = 'snapshot_date', 
    y = 'value', 
    color = 'variable', 
    facet_col = 'asset'
  )

  fig.update_layout(
    # plot_bgcolor = '#ffffff',
    margin = dict(l=20, r=20, t=20, b=20),
    height = 250, 
    width = 2000
  )

  return fig

def build_summary_text(portfolio_summary: PortfolioSummary) -> str:
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
ordered_assets = list(orders_df['asset'].unique())

selected_assets = st.sidebar.multiselect(
  label = 'Select Assets', 
  options = ordered_assets,
  default = ordered_assets
)

portfolio_data = PortfolioData(orders_df, assets = selected_assets)

# Title 
# ===========================================================================================
st.title('Portfolio Explorer')

# Text Summary
# ===========================================================================================
portfolio_summary = portfolio_data.summarize()
portfolio_summary_text = build_summary_text(portfolio_summary)
st.markdown(portfolio_summary_text)

# Portfolio Value Time Series
# ===========================================================================================
fig = plot_portfolio_value(portfolio_data)
st.plotly_chart(fig, use_container_width = True)

# Asset Value Time Series
# ===========================================================================================
fig = plot_asset_value(portfolio_data)
st.plotly_chart(fig, use_container_width = True)

# Return distribution
# ===========================================================================================
portfolio_returns = PortfolioReturns(portfolio_data)
inception_returns_snapshot = portfolio_returns.expected_returns_snapshot

p = sns.histplot(inception_returns_snapshot.loc['2015-01-01':])
plt.axvline(portfolio_summary.percent_return, color='darkred', ls='--')
st.pyplot(p.get_figure())
