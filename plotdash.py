from dash import Dash, dcc,html, callback, Output, Input
import pandas as pd
import plotly.express as px
import json, requests
from flask_app import *
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
# Read the transactions data from the JSON file
# Convert transactions data to a pandas DataFrame
data = query_transactions()
df = pd.DataFrame(data)

result = {}
for index, row in df.iterrows():
    key = row['user_id']
    value = {'transaction_id': row['transaction_id'], 'timestamp': row['timestamp'], 'account_type': row['account_type'], 'amount': row['amount'],
                      'account_id': row['account_id'], 'is_fraud': row['is_fraud']}
    result[key] = value

    tmp = []
    for key, value in result.items():
        data.append({'transaction_id': key, **value})

# Initialize the Dash app
dash_app = Dash(__name__)
def color_mapping(fraud):
    return 'salmon' if fraud else 'lightgreen'

# Create the layout of the Dash app
dash_app.layout = html.Div([
    html.H1('Fraud Detection App', style= {'color':'darkcyan'}),

    # Interactive table
    html.H2('Transactions Table'),
    dcc.Graph(
        id='transactions-table',
        figure=go.Figure(
            data=[
                go.Table(
                    header=dict(values=df.columns),
                    cells=dict(
                        values=df.values.transpose(),
                        fill=dict(color=[[color_mapping(fraud) for fraud in df['is_fraud']]])
                    )
                )
            ]
        )
    ),

    # Pie chart
    html.H2('Proportion of Fraud by Account Type'),
    dcc.Graph(
        id='fraud-pie-chart',
        figure=go.Figure(
            data=[
                go.Pie(
                    labels=df[df['is_fraud']]['account_type'],
                    values=[1] * len(df[df['is_fraud']]),
                    name='Proportion of Fraud by Account Type'
                )
            ]
        )
    )
])

# Run the Dash app
if __name__ == '__main__':
    dash_app.run_server(debug=True, port = 7070)
