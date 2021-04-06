import numpy as np
import pandas as pd
from pandas.core.tools.datetimes import to_datetime
import seaborn as sns
import matplotlib.pyplot as plt
import portfolio_design.src.edhec_risk_kit as erk

def compute_rolling_annualized_return(
  returns_df: pd.DataFrame,
  n_periods: int) -> pd.DataFrame:

  returns = []

  for w in returns_df.rolling(n_periods, closed = 'right'):
    period_ending = w.index.max()
    r = (
      erk
        .annualize_rets(w, periods_per_year = 12)
        .to_frame()
        .T
    )
    r.index = [period_ending]
    returns.append(r)

  annualized_returns_df = pd.concat(returns)
  annualized_returns_df.index.name = 'date'

  return annualized_returns_df

def compute_from_date(
  fn,
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None) -> pd.DataFrame:

  if to_date is None:
    to_date = returns_df.index.max()

  date_range = pd.date_range(from_date, to_date, freq = 'M')

  returns = []

  for d in date_range:
    r = (
      fn(
          returns_df.loc[from_date:d]
        )
        .to_frame()
        .T
    )
    
    r.index = [d]

    returns.append(r)

  annualized_returns_df = pd.concat(returns)
  annualized_returns_df.index.name = 'date'

  return annualized_returns_df

def compute_annualized_return_from_date(
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None) -> pd.DataFrame:

  if to_date is None:
    to_date = returns_df.index.max()

  date_range = pd.date_range(from_date, to_date, freq = 'M')

  returns = []

  for d in date_range:
    r = (
      erk
        .annualize_rets(
          returns_df.loc[from_date:d], 
          periods_per_year = 12)
        .to_frame()
        .T
    )
    
    r.index = [d]

    returns.append(r)

  annualized_returns_df = pd.concat(returns)
  annualized_returns_df.index.name = 'date'

  return annualized_returns_df
  
def plot_rolling_annualized_return(
  returns_df: pd.DataFrame,
  n_periods: int) -> pd.DataFrame:

  facet_plot_df = (
    compute_rolling_annualized_return(returns_df, n_periods)
      .reset_index()
      .assign(
        period = lambda df: df['date'].apply(
          lambda d: 'pre-covid' if d <= pd.to_datetime('2020-03-01') else 'post-covid'
        )
      )
      .melt(id_vars = ['date', 'period'], var_name = 'ticker', value_name = 'return')
  )

  f = sns.relplot(
    x = 'date',
    y = 'return',
    kind = 'line',
    col = 'ticker',
    hue = 'period',
    data = facet_plot_df,
    col_wrap = 3
  );

  f.map(plt.axhline, y = 0, ls = '--', color = 'darkgrey');

  return facet_plot_df

def plot_annualized_return_from_date(
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None):

  facet_plot_df = (
    compute_annualized_return_from_date(returns_df, from_date, to_date)
      .reset_index()
      .assign(
        period = lambda df: df['date'].apply(
          lambda d: 'pre-covid' if d <= pd.to_datetime('2020-03-01') else 'post-covid'
        )
      )
      .melt(id_vars = ['date', 'period'], var_name = 'ticker', value_name = 'return')
  )

  f = sns.relplot(
    x = 'date',
    y = 'return',
    kind = 'line',
    col = 'ticker',
    hue = 'period',
    data = facet_plot_df,
    col_wrap = 3
  );

  f.map(plt.axhline, y = 0, ls = '--', color = 'darkgrey');

def plot_from_date(
  fn,
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None):

  facet_plot_df = (
    compute_from_date(fn, returns_df, from_date, to_date)
      .reset_index()
      .assign(
        period = lambda df: df['date'].apply(
          lambda d: 'pre-covid' if d <= pd.to_datetime('2020-03-01') else 'post-covid'
        )
      )
      .melt(id_vars = ['date', 'period'], var_name = 'ticker', value_name = 'value')
  )

  f = sns.relplot(
    x = 'date',
    y = 'value',
    kind = 'line',
    col = 'ticker',
    hue = 'period',
    data = facet_plot_df,
    col_wrap = 3
  );

  f.map(plt.axhline, y = 0, ls = '--', color = 'darkgrey');

def compute_corr_from_date(
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None) -> pd.DataFrame:

  if to_date is None:
    to_date = returns_df.index.max()

  date_range = pd.date_range(from_date, to_date, freq = 'M')

  corrs = []

  for d in date_range:

    corr = returns_df.loc[from_date:d].corr()
    mask = np.triu(corr).astype(bool)
    df = corr.where(mask)
    df = df.stack().reset_index()
    df.columns = ['ticker_a', 'ticker_b', 'corr']
    df = df.query('ticker_a != ticker_b').copy()
    df['date'] = d

    corrs.append(df)

  corrs_df = pd.concat(corrs)

  return corrs_df

def plot_corr_from_date(
  returns_df: pd.DataFrame,
  from_date: str,
  to_date: str = None):

  facet_plot_df = compute_corr_from_date(
    returns_df,
    from_date,
    to_date)

  f = sns.relplot(
    x = 'date',
    y = 'corr',
    kind = 'line',
    col = 'ticker_a',
    row = 'ticker_b',
    # hue = 'period',
    data = facet_plot_df,
    # col_wrap = 3
  );

  f.map(plt.axhline, y = 0.5, ls = ':', color = 'darkgrey');
  f.map(plt.axhline, y = 0.5, ls = '--', color = 'darkgrey');