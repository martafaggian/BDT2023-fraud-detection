from flask import Flask
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd


app3 = Flask(__name__)


dash_app = Dash(__name__, server=app3, suppress_callback_exceptions=True, external_stylesheets= [dbc.themes.SOLAR],
            url_base_pathname='/')

df = pd.read_csv('transactions.csv')
data = df[['user_id','transaction_id', 'timestamp', 'amount', 'account_type', 'account_id','is_fraud']]
users = data['user_id'].unique()

fraud_row_style = {'background-color': 'salmon', 'color': 'white'}
non_fraud_row_style = {'background-color': 'green', 'color': 'white'}

dash_app.layout = dbc.Container([html.Div([
    html.H2('Select your user ID'),
    dcc.Dropdown(
        id='user-dropdown',
        options=[{'label': user, 'value': user} for user in users]
    ),
    html.Table([
        html.Thead([
            html.Tr([
                html.Th('Transaction ID'),
                html.Th('Account Type'),
                html.Th('Timestamp'),
                html.Th('Is Fraud')
            ])
        ]),
        html.Tbody(id='transactions-table')
    ], className='table table-striped'
    ),

])])


@dash_app.callback(
    Output('transactions-table', 'children'),
    Input('user-dropdown', 'value')
)
def update_transactions_table(user_id):
    if user_id is None:
        return []
    transactions = data.loc[data['user_id'] == user_id]

    rows = []
    for index, row in transactions.iterrows():
        row_style = fraud_row_style if row['is_fraud'] else non_fraud_row_style
        rows.append(html.Tr([
            html.Td(row['transaction_id'], style=row_style),
            html.Td(row['account_type'],style=row_style),
            html.Td(row['timestamp'],style=row_style),
            html.Td(str(row['is_fraud']),style=row_style)
        ]))
    return  rows


if __name__ == '__main__':
    app3.run(debug=True,port= 2070 )
