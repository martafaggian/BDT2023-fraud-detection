from flask import Flask, redirect
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

app_flask1 = Flask(__name__)
external_stylesheets = [dbc.themes.SOLAR]
app1 = Dash(__name__, server=app_flask1, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
           url_base_pathname='/')

data = pd.read_csv('transactions.csv')
users = data['user_id'].unique()

app1.layout = html.Div([
    dbc.Container([
        dbc.Row([

            html.H1(["Welcome to DetectiveFraud"]),
            html.H2(["Keep your transactions safe from thieves!"
        ]),html.P('', style={'margin-bottom': '20px'}),]),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("GitHub", href="https://github.com/martafaggian/BDT2023-fraud-detection")),
                dbc.DropdownMenu(
                    children=[

                        dbc.DropdownMenuItem("Settings", href="https://www.eba.europa.eu/contacts"),
                        dbc.DropdownMenuItem("FAQ", href="https://www.eba.europa.eu/single-rule-book-qa/search"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="More",
                ),
            ],
            brand="Start your Research!",
            brand_href="#",
            color="primary",
            dark=True,
        ),html.P('', style={'margin-bottom': '20px'}),
    dbc.Row(
                [
                    dbc.Label("Email", width="auto"),
                    dbc.Col(
                        dbc.Input(type="email", placeholder="Enter email"),
                        className="me-3",
                    ),
                    dbc.Label("Password", width="auto"),
                    dbc.Col(
                        dbc.Input(type="password", placeholder="Enter password"),
                        className="me-3",
                    ),
                    dbc.Col(html.A(dbc.Button("Submit", id='flask-dash-app-btn',color="primary", href='http://localhost:1111'))),
                ],
                className="g-2"),html.P('', style={'margin-bottom': '20px'}),

            dbc.Row([
                html.H4(['You can also search just with your user ID'])
            ]),

            dbc.Row([
                html.Div([
                    dbc.Button("Go to Selection", color="primary", className="me-1", href='http://localhost:2070/')
                ])
            ])
,html.P('', style={'margin-bottom': '20px'}),
        dbc.Row([
            dbc.Alert(
                [
                    "This is a prototype. For further information ",
                    html.A("click here", href="https://dash.plotly.com/", className="alert-link"),
                ],
                color="info",
            )
        ]),
        dbc.Row([
                    html.Div([
                    html.Img(src="https://cdn.pixabay.com/photo/2022/03/13/01/36/fraud-7065116_1280.png")
])])

        ])])


@app1.callback(
    [Output("email-input", "valid"), Output("email-input", "invalid")],
    [Input("email-input", "value")],
)
def check_validity(text):
    if text:
        is_gmail = text.endswith("@gmail.com")
        return is_gmail, not is_gmail
    return False, False


@app_flask1.route('/')
def homepage():
    return redirect('/')


if __name__ == "__main__":
    app_flask1.run(debug=True, port= 5050)
