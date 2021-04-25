import pandas as pd

import portfolio_design.src.edhec_risk_kit as erk
import portfolio_design.src.analysis as an
from portfolio_design.src import data

# asset_1mo_returns_df = data.compute_monthly_returns_from_mmd(asset_market_data_df)
# asset_1mo_returns_df.index = asset_1mo_returns_df.index + pd.DateOffset(months = -1)
# asset_2mo_returns_df = data.compute_monthly_returns_from_mmd(asset_market_data_df)
# asset_2mo_returns_df.index = asset_2mo_returns_df.index + pd.DateOffset(months = -2)
# asset_3mo_returns_df = data.compute_period_returns_from_mmd(asset_market_data_df, periods = 3)
# asset_3mo_returns_df.index = asset_3mo_returns_df.index + pd.DateOffset(months = -3)
# asset_6mo_returns_df = data.compute_period_returns_from_mmd(asset_market_data_df, periods = 6)
# asset_6mo_returns_df.index = asset_6mo_returns_df.index + pd.DateOffset(months = -6)
# asset_12mo_returns_df = data.compute_period_returns_from_mmd(asset_market_data_df, periods = 12)
# asset_12mo_returns_df.index = asset_12mo_returns_df.index + pd.DateOffset(months = -12)
# asset_24mo_returns_df = data.compute_period_returns_from_mmd(asset_market_data_df, periods = 24)
# asset_24mo_returns_df.index = asset_24mo_returns_df.index + pd.DateOffset(months = -24)

# data.compute_period_returns_from_mmd(asset_market_data_df, periods = 24)

def make_monthly_asset_data(symbols: str) -> dict:
  
  asset_df = (
    data
      .get_monthly_market_data(symbols, interval = '1mo')
  )

  months = [1, 2, 3, 6, 12, 14]

  def make_return_df(n_months: int): 
    r_df = data.compute_period_returns_from_mmd(asset_df, periods = n_months)
    r_df.index = r_df.index + pd.DateOffset(months = -n_months)
    return r_df

  dfs = {}

  for month in months:
    dfs[month] = make_return_df(month)

  return dfs