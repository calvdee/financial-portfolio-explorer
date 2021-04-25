# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from re import M
import sys, os

from dash_html_components.Br import Br
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

from portfolio_builder.src.portfolios import Portfolio
from portfolio_builder.src.data import get_asset_returns_data
from dash.dependencies import Input, Output

# Data
# ======================================================================================================
portfolio_dfs = get_asset_returns_data([
  'SOXX',
  'COST',
  'DHR'
])


# UI
# ======================================================================================================
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# App
# ======================================================================================================
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create server variable with Flask server object for use with gunicorn
server = app.server

row_style = {
  'borderBottom': 'thin lightgrey solid',
  'backgroundColor': 'rgb(250, 250, 250)',
  'padding': '10px 5px'
}

app.layout = html.Div([
    html.Div([
      html.Div([
        html.H1('Configuration'),
        html.Br(),
        html.I("How much capital do you have to invest?"),
        html.Br(),
        dcc.Input(id="capital", type="text", placeholder="")
      ], style = row_style),
      # html.Div([
      #   html.I("What is your target return?"),
      #   html.Br(),
      #   dcc.Input(id="target_return", type="text", placeholder="")
      # ], style = row_style),
      html.Div([
        html.I("Specify an asset list:"),
        html.Br(),
        dcc.Input(id="asset_names", type="text", placeholder="")
      ], style = row_style),
      html.Button('Run', id='run', n_clicks = 0)
    ]),
    html.Div([
      html.I(id = 'output')
    ]),
    html.Div([
      html.Br(),
      html.H1('Allocation'),
      dcc.Graph(id='allocation-graph', style = {'padding': '10px'}),
    ]),
])

def build_allocation_big_nums(portfolio: Portfolio, capital: float):
  fig = go.Figure()

  for ix, w in enumerate(portfolio.weights):
    print(type(w))
    print(type(capital))

    fig.add_trace(go.Indicator(
      mode = "number",
      value = w,
      domain = {'row': 0, 'column': ix},
      title = portfolio.asset_names[ix],
      number = {
        'valueformat': '%'
      }
    ))

    fig.add_trace(go.Indicator(
      mode = "number",
      value = w * capital,
      domain = {'row': 1, 'column': ix},
      number = {
        'valueformat': '$.0f'
      }
    ))
    
  fig.update_layout(
    grid = {'rows': 2, 'columns': len(portfolio.asset_names), 'pattern': "independent"},
    width = 500, 
    margin = dict(l = 20, r = 20, t = 50, b = 20),
    height = 150,
    autosize = True
  )

  return fig

@app.callback(
    Output('allocation-graph', 'figure'),
    [dash.dependencies.Input('run', 'n_clicks')],
    [dash.dependencies.State('asset_names', 'value')],
    [dash.dependencies.State('capital', 'value')]
  )
def update_allocation_view(n_clicks, asset_names: str, capital: float):
  if n_clicks == 0:
    return go.Figure()
  
  asset_names = asset_names.split(',')
  portfolio = Portfolio(asset_names)

  return build_allocation_big_nums(portfolio, float(capital))


if __name__ == '__main__':
    app.run_server(debug=True)