import plotly.graph_objects as go
import plotly.express as px
from src.portfolio import PortfolioData

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
    margin = dict(l=5, r=5, t=5, b=0)
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

  # fig.update_xaxes(matches=None)

  return fig