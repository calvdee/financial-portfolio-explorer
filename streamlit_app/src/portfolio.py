import pandas as pd
import numpy as np
from src import data
from dataclasses import dataclass, field
from typing import List

@dataclass
class PortfolioSummary:
  dollar_cost: float
  dollar_value: float
  annualized_return: float
  dollar_return: float = field(init = False)
  percent_return: float = field(init = False)

  def __post_init__(self):
    self.dollar_return = self.dollar_value - self.dollar_cost
    self.percent_return = self.dollar_value / self.dollar_cost - 1


class PortfolioData(object):
  """
  A portfolio defined by a set of assets
  """
  def __init__(self, orders_df: pd.DataFrame, assets: List[str] = None):
    portfolio_assets = assets or list(orders_df['asset'].unique())
    self.assets = portfolio_assets

    prices_df = data.make_prices_df(self.assets)
    self.prices_snapshot = (
      prices_df
        .query('asset in @portfolio_assets')
        .set_index('price_date')
        .sort_index()
    )

    self.order_snapshot = data.make_order_value_snapshot_df(
      prices_df,
      orders_df
    ).query('asset in @portfolio_assets').set_index('order_date').sort_index()
    
    self.asset_snapshot = (
      data.make_asset_value_snapshot_df(self.order_snapshot)
        .set_index('snapshot_date')
        .sort_index()
    )
    
    self.portfolio_snapshot = (
      data.make_portfolio_value_snapshot_df(self.asset_snapshot)
        .set_index('snapshot_date')
        .sort_index()
    )
    
    returns = (
      self.portfolio_snapshot['portfolio_value_usd'] / 
        self.portfolio_snapshot['portfolio_cost_usd'] - 1
    ).rename('return').to_frame()

    self.returns_snapshot = (
      returns
        .assign(
          return_period_days = lambda df: (df.index - df.index.min()).days
        )
    )
  
  def summarize(self) -> PortfolioSummary:
    portfolio_state = (
      self.portfolio_snapshot
        .sort_index()
        .tail(1)
    )

    portfolio_cost = portfolio_state['portfolio_cost_usd'].values[0]
    portfolio_value = portfolio_state['portfolio_value_usd'].values[0]

    return PortfolioSummary(
      dollar_cost = portfolio_cost,
      dollar_value = portfolio_value
    )

  @property
  def days_since_inception(self) -> int:
    days = (
      self.portfolio_snapshot.index.max() - 
        self.portfolio_snapshot.index.min()
    ).days

    return days

  @property
  def current_allocation(self) -> np.array:
    asset_snapshot_cost_wide = (
      self
        .asset_snapshot
        .pivot(columns = 'asset', values = 'asset_cost_usd')
    )

    assest_value_allocation_snapshot_wide = asset_snapshot_cost_wide.div(
      self.portfolio_snapshot['portfolio_value_usd'],
      axis = 0
    )

    current_allocation = (
      assest_value_allocation_snapshot_wide
        .tail(1)
        .squeeze()
    )

    return current_allocation