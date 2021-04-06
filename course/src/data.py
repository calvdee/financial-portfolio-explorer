import pandas as pd

def get_ffme_returns() -> pd.DataFrame:
  returns = (
    pd.read_csv(
      '../data/Portfolios_Formed_on_ME_monthly_EW.csv',
      na_values = -99.99,
      index_col = 0
    )
    [['Lo 10', 'Hi 10']]
    .apply(lambda col: col / 100)
  )
  
  returns.columns = ['small_cap', 'large_cap']
  
  return returns

def get_hfi_returns():
  hfi = (
    pd.read_csv(
      '../data/edhec-hedgefundindices.csv',
      parse_dates = True,
      index_col = 0
    )
    .apply(lambda col: col / 100)
  )

  hfi.index = hfi.index.to_period('M')

  return hfi

def get_industry_monthly_returns():
  returns_df = (
    pd.read_csv(
      '../data/ind30_m_vw_rets.csv',
      parse_dates = True,
      index_col = 0
    )
    .apply(lambda col: col / 100)
  )

  returns_df.index = pd.to_datetime(
    returns_df.index,
    format = '%Y%m'
  ).to_period('M')

  returns_df.columns = returns_df.columns.str.strip()

  return returns_df
