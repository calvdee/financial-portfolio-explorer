import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import analysis as an

from data import get_monthly_market_data

ticker = st.sidebar.text_input(label = 'Ticker:')


if ticker != '':
  monthly_returns_df = get_monthly_market_data(
    tickers = [ticker],
    interval = '1mo',
    returns_only = False
  )
  fig, axs = plt.subplots(figsize = (20, 7), nrows = 1, ncols = 3)
  
  monthly_returns_df['adjusted_close'].ffill().plot(ax = axs[0]);
  axs[0].axvline('2020-03-01', color = 'darkred');

  monthly_returns_df['period_return'].plot(ax = axs[1]);
  axs[1].axvline('2020-03-01', color = 'darkred');

  sns.histplot(monthly_returns_df['period_return'], ax = axs[2])

  st.pyplot(fig)

  years = monthly_returns_df.index.year.unique()
  ars = []

  for year in years:
    ar = an.annualized_return(monthly_returns_df.loc[str(year):, 'period_return'])
    ars.append(ar)

  fig = plt.figure()
  annualized_returns = pd.Series(ars, index = years)
  annualized_returns.plot();
  st.pyplot(fig)

  at = an.annualized_return(monthly_returns_df['period_return'])
  st.write(f'Expected annualized return:', at)