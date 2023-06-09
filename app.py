from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

data = pd.read_csv('transactions.csv')


external_stylesheets = [dbc.themes.QUARTZ]
app = Dash(__name__, external_stylesheets=external_stylesheets)

fig = px.histogram(data, x="account_id", y="amount", color="fraud_confidence", barmode="group")


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.H1(["Welcome to DetectiveFraud"]),
                html.H2(["Keep your transactions safe from thieves!"


            ])]),
        dbc.Col([


dbc.ButtonGroup(
    [
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Contacts", href="#"), dbc.DropdownMenuItem("Settings", href="#")],
            label="Menu",
            group=True,
            color='info',
        ),
    ],
    vertical=True,

),
], width= 6),
        dbc.Col([

dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="dark", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

]),

        dbc.Row(
            [
                dbc.AccordionItem(
                                [
                                    html.P("To check your personal info"),
                                    dbc.Button("Login",color='primary',
                                               href="#"),
                                ],
                                title="User Portal",
                            ),

                dbc.AccordionItem(
                    [
                        html.P("To check your bank info"),
                        dbc.Button("Login ", color="success",
                                   href="#"),
                    ],
                    title="Bank Portal"),
]),
    dbc.Row([

html.Div(children='''
        
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )



    ])])

if __name__ == "__main__":
    app.run_server(debug=True,port = 8888)
