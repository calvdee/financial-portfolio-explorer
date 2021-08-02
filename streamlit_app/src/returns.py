import pandas as pd

from src.portfolio import PortfolioData

_ix = pd.IndexSlice

def compute_period_returns(periodic_snapshot: pd.DataFrame, periods: int) -> pd.DataFrame:
  return periodic_snapshot.pct_change(periods)

def annualize_returns(returns: pd.Series, periods_per_year: int):
  growth_product = (1+returns).prod()
  n_periods = returns.shape[0]
  return growth_product**(periods_per_year/n_periods)-1

class PortfolioReturns(object):
  def __init__(self, portfolio_data: PortfolioData):
    self.portfolio_data = portfolio_data
  
  @property
  def expected_returns_snapshot(self) -> pd.DataFrame:
    wide_prices_snapshot = (
      self.portfolio_data
        .prices_snapshot
        .pivot(columns = 'asset', values = 'unit_price_usd')
    )

    inception_returns_snapshot = compute_period_returns(
      periodic_snapshot = wide_prices_snapshot,
      periods = self.portfolio_data.days_since_inception
    )

    current_allocation = self.portfolio_data.current_allocation

    expected_returns_snapshot = (
      inception_returns_snapshot
        .multiply(current_allocation, axis = 1)
        .sum(axis = 1)
    )
    
    return expected_returns_snapshot