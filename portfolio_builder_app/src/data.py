from portfolio_builder.src.assets import make_monthly_asset_data
from portfolio_builder.src.portfolios import Portfolio

def get_asset_returns_data(portfolio: list):
  dfs = make_monthly_asset_data(portfolio)
  return dfs

def get_portfolio(symbols: str, weights = None):
  return Portfolio(symbols, weights)