import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass
class Portfolio(object):
  asset_names: list
  weights: np.array = None

  def __post_init__(self):
    if self.weights is None: 
      self.weights = np.repeat(
        1 / len(self.asset_names),
        repeats = len(self.asset_names)
      )

  def make_returns_data(self) -> pd.DataFrame:
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
