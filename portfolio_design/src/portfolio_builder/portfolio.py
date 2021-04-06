import pandas as pd
from typing import List
from portfolio_design.src import data
from portfolio_design.src import edhec_risk_kit as erk

class Portfolio(object):
  def __init__(
    self, 
    assets: List[str],
    return_periods: List[int] = [1, 3, 6, 12, 24, 36]):

    self.assets = assets
    self.return_periods = return_periods
    self.monthly_market_data = data.get_monthly_market_data(
      tickers = self.assets,
      interval = '1mo'
    )
    self.returns_data = self._build_returns_data()

  def _group_by_asset(self, asset_df: pd.DataFrame, period: int):
    return (
      asset_df
        .query(f'Period == "{period} Month"')
        .groupby('Asset')
    )


  def _build_returns_data(self) -> pd.DataFrame:
    dfs = []

    for period in self.return_periods:
      r_df = (
        data
        .compute_period_returns_from_mmd(
          self.monthly_market_data,
          period
        )
        .melt(
          ignore_index = False,
          var_name = 'Asset',
          value_name = 'Return'
        )
        .assign(Period = f'{period} Month')
        .dropna()
      )
      
      dfs.append(r_df)
    
    return pd.concat(dfs)
  
  def compute_return_stats(self, period: int, as_percent: bool = False):
    return (
      self
        ._group_by_asset(self.returns_data, period)
        ['Return']
        .describe()
        .round(3)
        .multiply(100 if as_percent else 1)
        .assign(
          n_years = lambda df: (df['count'] / (12 * 100 if as_percent else 1)).round(1)
        )
        .drop(columns = 'count')
        .sort_values('mean', ascending = False)
    )
  
  def compute_annualized_returns(self,
    from_date: str,
    to_date: str = None,
    as_percent: bool = False,
    n_annual_periods: int = 1):

    returns = self.returns_data.loc[from_date:]

    if to_date is not None:
      returns = returns.loc[:to_date]
    
    return (
      self._group_by_asset(returns, 1)
        ['Return']
        .apply(erk.annualize_rets, periods_per_year = 12 * n_annual_periods)
        .round(3)
        .multiply(100 if as_percent else 1)
        .sort_values(ascending = False)
    )

  def compute_risk_adjusted_returns(self,
    from_date: str,
    riskfree_rate: float,
    to_date: str = None,
    as_percent: bool = False,
    n_annual_periods: int = 1):

    returns = self.returns_data.loc[from_date:]

    if to_date is not None:
      returns = returns.loc[:to_date]
    
    return (
      self._group_by_asset(returns, 1)
        ['Return']
        .apply(erk.sharpe_ratio, periods_per_year = 12 * n_annual_periods, riskfree_rate = riskfree_rate)
        .round(3)
        .multiply(100 if as_percent else 1)
        .sort_values(ascending = False)
    )

  def compute_volatility(self, period: int, as_percent: bool = False):
    grouped = self._group_by_asset(self.returns_data, period)['Return']

    semi_deviation = grouped.apply(erk.semideviation).rename('semi_deviation')
    cvar_historic = grouped.apply(erk.cvar_historic).rename('cvar_historic')
    var_historic = grouped.apply(erk.var_historic).rename('var_historic')
    var_gaussian = grouped.apply(erk.var_gaussian, modified = True).rename('var_gaussian')

    volatility = pd.concat([
      semi_deviation,
      cvar_historic,
      var_historic,
      var_gaussian
    ], axis = 1)

    return (
      volatility
        .round(3)
        .multiply(100 if as_percent else 1)
        .sort_values('semi_deviation', ascending = False)
    )
  

  def compute_annualized_volatility(self,
    from_date: str,
    to_date: str = None,
    as_percent: bool = False,
    n_annual_periods: int = 1):

    returns = self.returns_data.loc[from_date:]

    if to_date is not None:
      returns = returns.loc[:to_date]
    
    return (
      self._group_by_asset(returns, 1)
        ['Return']
        .apply(erk.annualize_vol, periods_per_year = 12 * n_annual_periods)
        .round(3)
        .multiply(100 if as_percent else 1)
        .sort_values(ascending = False)
    )