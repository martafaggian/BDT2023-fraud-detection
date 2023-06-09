from flask import Flask
from omegaconf import OmegaConf
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from app.infrastructure import Database


app3 = Flask(__name__)

dash_app = Dash(__name__, server=app3, suppress_callback_exceptions=True, external_stylesheets= [dbc.themes.SOLAR],
            url_base_pathname='/')

conf = OmegaConf.load('config.yaml')
db = Database.from_conf("cassandra-web", conf.cassandra, conf.logs)
data = pd.DataFrame(db.execute("""
    SELECT user_id, transaction_id,
    timestamp, amount, account_type,
    account_id, is_fraud FROM
    fraud_detection.transactions"""))

users = data.user_id.unique()

# There may be a lot of users with empty transactions. For a real
# system, use the following:
# users = pd.DataFrame(db.execute("""
    # SELECT user_id FROM
    # fraud_detection.users
# """)).user_id.values 

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
    transactions = pd.DataFrame(db.execute(f"""
        SELECT user_id, transaction_id,
        timestamp, amount, account_type,
        account_id, is_fraud FROM
        fraud_detection.transactions_by_user
        WHERE user_id = '{user_id}' ALLOW FILTERING"""))

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
    app3.run(host="0.0.0.0", debug=True,port= 2070 )
