from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field
import pandas as pd
import yfinance as yf

ix = pd.IndexSlice

def load_orders(path: str) -> pd.DataFrame:
  """
  Loads order data

  Parameters
  ----------
  path : str
      The path to the orders CSV file

  Returns
  -------
  pd.DataFrame
      A dataframe of orders indexed by an auto-incrementing order ID
  """
  orders_df = (
    pd
      .read_csv(path, parse_dates = ['order_date'])
      .reset_index()
      .rename(columns = {'index': 'order_id'})
      .assign(
        order_id = lambda df: df['order_id']+1,
        order_date = lambda df: pd.to_datetime(df['order_date'].dt.date)
      )
  )

  return orders_df

def get_market_data(
  symbols: list, 
  interval: str) -> pd.DataFrame:

  mmd_df = (
    yf
      .download(tickers = symbols, end = datetime.now(), interval=interval)
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

def make_orders_df(orders: List[Dict[str, any]]) -> pd.DataFrame:
  orders_df = (
    pd
      .DataFrame(orders)
      .assign(
        order_cost_usd = lambda df: df['order_units'] * df['unit_cost_usd']
      )
  )

  return orders_df

def make_prices_df(assets: List[str]) -> pd.DataFrame:
  market_data_df = (
    get_market_data(assets, interval = '1d')
  )

  prices_df = (
    ((market_data_df['adjusted_close'] + market_data_df['open']) / 2)
      # Move date to columns
      .reset_index()
      .melt(
        id_vars = ['date'],
        value_name = 'unit_price_usd',
        var_name = 'asset'
      )
      # Sort for the following groupby to work
      .sort_values(by = 'date')
      # Now we need to make sure we don't have any gaps resulting
      # from different holidays in different markets. For example,
      # Memorial Day in the US (May 31) results in no price records for
      # US-based equities but there are price records for TSX-based
      # assets.
      .assign(unit_price_usd = lambda df: 
        df
          .groupby('asset')
          ['unit_price_usd']
          .transform(lambda grp: grp.ffill())
      )  
      .rename(columns = {'date': 'price_date'})
  )

  if len(assets) == 1:
    prices_df = prices_df.assign(
      asset = assets[0]
    )

  return prices_df

def make_order_value_snapshot_df(
  prices_df: pd.DataFrame,
  orders_df: pd.DataFrame
) -> pd.DataFrame:

  order_value_snapshot_df = (
    prices_df
      # Cross-join on the orders to get one row per order
      # per day
      .merge(
        orders_df[['asset', 'order_date', 'order_id', 'order_units', 'order_cost_usd']],
        how = 'inner',
        on = ['asset'],
        indicator = True
      )
      # Only include records where the `price_date` is on or after the
      # `order_date`. This would be implemented as a range join in SQL.
      .query('price_date >= order_date')
      .assign(
        order_value_usd = lambda df: df['order_units'] * df['unit_price_usd']
      )
      [[
        'asset',
        'price_date',
        'order_date',
        'order_id',
        'order_units',
        'unit_price_usd',
        'order_cost_usd',
        'order_value_usd'
      ]]
      # Since we melted the market data dataframe, we'll have one
      # record for every date from the min date to the max date
      # over all assets, so lots of NULL unit_price_usd values in
      # some cases
      .dropna(subset = ['unit_price_usd'])
  )

  return order_value_snapshot_df

def make_asset_value_snapshot_df(order_value_snapshot_df: pd.DataFrame) -> pd.DataFrame:
  asset_value_snapshot_df = (
    order_value_snapshot_df
      .groupby(['asset', 'price_date'])
      .agg(
        asset_cost_usd = pd.NamedAgg('order_cost_usd', 'sum'),
        asset_value_usd = pd.NamedAgg('order_value_usd', 'sum')
      )
      .reset_index()
      [[
        'asset',
        'price_date',
        'asset_cost_usd',
        'asset_value_usd'
      ]]
      .rename(columns = {'price_date': 'snapshot_date'})
  )

  return asset_value_snapshot_df

def make_portfolio_value_snapshot_df(
  asset_value_snapshot_df: pd.DataFrame
) -> pd.DataFrame:
  portfolio_value_snapshot_df = (
    asset_value_snapshot_df
      .groupby(['snapshot_date'])
      .agg(
        portfolio_cost_usd = pd.NamedAgg('asset_cost_usd', 'sum'),
        portfolio_value_usd = pd.NamedAgg('asset_value_usd', 'sum'),
      )
      .reset_index()
  )

  return portfolio_value_snapshot_df
  
