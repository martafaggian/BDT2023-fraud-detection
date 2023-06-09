"""
# === OVERVIEW === #
This Python file uses Flask and Dash to create a web page where a client can access information for a specific user ID. 
After selecting the user ID, a table is displayed containing the variables ‘transaction_id’, ‘timestamp’, ‘amount’, ‘account_type’, ‘account_id’, and ‘is_fraud’. 
For visual clarity, the rows in the table are color-coded based on the value of the ‘is_fraud’ variable.
Firstly, we import the required modules and libraries. After that, we initialize the app through the Dash() function.
"""
from flask import Flask
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

"""
# === FLASK AND  DASH APPLICATION INITIALIZATION AND CONFIGURATION === #
The code initializes a Flask application (app3) using the Flask class from the flask module. Then, a Dash application (dash_app) is set using the Dash class from the dash module. 
The Flask application (app3) is passed as the server parameter to enable integration between Flask and Dash.
-	The suppress_callback_exceptions parameter is set to True, which allows the Dash application to display custom error messages when callback exceptions occur.
-	The external_stylesheets parameter is set to [dbc.themes.SOLAR], which applies the Solar theme from the dash_bootstrap_components library to the Dash application.
-	The url_base_pathname parameter is set to "/", specifying the base URL pathname for the Dash application.
"""
app3 = Flask(__name__)

dash_app = Dash(__name__, server=app3, suppress_callback_exceptions=True, external_stylesheets= [dbc.themes.SOLAR],
            url_base_pathname='/')

"""
 # === DATA LOADING AND PREPARATION === #
The code reads transaction data from a CSV file named transactions.csv using the pd.read_csv() function from the pandas library. 
It selects specific columns from the data and assigns it to a DataFrame called data. The unique user IDs from the user_id column are extracted and stored in the users variable.

"""

df = pd.read_csv('transactions.csv')
data = df[['user_id','transaction_id', 'timestamp', 'amount', 'account_type', 'account_id','is_fraud']]
users = data['user_id'].unique()

# For visual purposes: salmon if is labeled as fraud, green otherwise
fraud_row_style = {'background-color': 'salmon', 'color': 'white'}
non_fraud_row_style = {'background-color': 'green', 'color': 'white'}

"""
# === DASH APPLICATION LAYOUT === #
The Dash application layout is defined using the dash_app.layout attribute. It contains the following components:
-	A dropdown component (dcc.Dropdown) for selecting a user ID.
-	A table component (html.Table) for displaying transaction details.
-	The table includes table headers (html.Thead) and table body (html.Tbody) components.
-	The table body has an ID (transactions-table) that will be updated dynamically based on user selection.

"""

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

"""
# === DASH CALLBACK FUNCTION === #
A Dash callback function is defined using the dash_app.callback decorator. This function is triggered when the value of the user dropdown component (user-dropdown) changes.
It then takes the selected user ID as an input (user_id.
If a user ID is selected, the code filters the data DataFrame to retrieve transactions related to that user. 
It iterates over the filtered transactions, creates table rows (html.Tr), and appends them to a list (rows). 
The style of each row is determined based on the fraud status of the transaction. ). If no user ID is selected, an empty list is returned.
The list of rows is then returned as the updated content for the transactions-table component.
"""

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
"""
# === FLASK ROUTE AND EXECUTION === #
The code defines a Flask route ("/") using the @app3.route decorator. 
When a user accesses the root URL ("/"), the associated function, hello_user(), is called. However, in this case, the function is not defined.
The code also includes a conditional statement, `if __name__ == '__main__':`, to ensure that the Flask application only runs if the current module is being executed as the main script.
Within this conditional block, the Flask application (app3) is run using the `run()` method. 
The application operates in debug mode, which enables detailed error messages, and listens on port 2070.
"""

if __name__ == '__main__':
    app3.run(debug=True,port= 2070 )
