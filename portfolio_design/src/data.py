from datetime import datetime
import pandas as pd
import yfinance as yf

ix = pd.IndexSlice

def get_monthly_market_data(
  tickers: list, 
  interval: str) -> pd.DataFrame:
  
  mmd_df = (
    yf
      .download(tickers = tickers, end = datetime.now(), interval=interval)
      .reset_index()
      .assign(date = lambda df: pd.to_datetime(df['Date']))
      .drop(columns = 'Date')
      .set_index('date')
      [['Open', 'Close', 'Adj Close']]
      .rename(columns = {
        'Open': 'open',
        'Close': 'close',
        'Adj Close': 'adjusted_close'
      })
      .dropna(how = 'all')
  )

  return mmd_df

def compute_monthly_returns_from_mmd(mmd_df: pd.DataFrame) -> pd.DataFrame:
  return mmd_df.loc[:, ix['adjusted_close']] / mmd_df.shift().loc[:, ix['adjusted_close']] - 1

def compute_period_returns_from_mmd(mmd_df: pd.DataFrame, periods: int) -> pd.DataFrame:
  return mmd_df.loc[:, ix['adjusted_close']] / mmd_df.shift(periods).loc[:, ix['adjusted_close']] - 1

def make_yearly_returns(closes: pd.Series) -> pd.Series:
  years = closes.index.year.unique()
  last_months = [f'{year}-12-01' for year in years[:-1]]
  annual_closing = closes.loc[last_months]
  return (annual_closing.shift() / annual_closing)
