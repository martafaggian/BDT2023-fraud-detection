"""
# === OVERVIEW === #
The code snippet demonstrates the implementation of a web application using Flask and Dash frameworks. 
It creates a web interface for a fraud detection system called "DetectiveFraud" that helps users keep their transactions safe from thieves. 
The application allows users to enter their email and password to log in and provides a link to search using their user ID. 
The layout includes a navigation bar, input fields for email and password, a submit button, and a link to the selection page. 
The code also defines a callback function to validate the email input.

# === LIBRARIES === #
Firstly, we import the necessary modules and libraries:
-          flask: A web framework for creating server-side applications. With redirect() a response object (namely, a WSGI application) is returned and 
                  it redirects the client to the target location
-          dash: A framework for building interactive web applications. Some additional components are used:
                -     Dash HTML Components (html) is used to access HTML tags
                -     Input and  Output that hold properties for specificied components
        
-          dash_bootstrap_components: A library providing Bootstrap-themed Dash components.
-          pandas: A library for data manipulation and analysis.

These dependencies can be installed by using the following command:

             pip install flask dash dash_bootstrap_components pandas
"""

from flask import Flask, redirect
from dash import Dash, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

""""
# === INITIALIZATION === #
The Flask and Dash applications are initialized using the following steps:
-          An instance of the Flask application (app_flask1) is created.
-          The external stylesheets are defined using dash_bootstrap_components's SOLAR theme.
-          An instance of the Dash application (app1) is created, with the Flask application as the server.
-          The URL base pathname is set to / for the Dash application. 
""""

app_flask1 = Flask(__name__)
external_stylesheets = [dbc.themes.SOLAR]
app1 = Dash(__name__, server=app_flask1, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
           url_base_pathname='/')
"""
The code reads transaction data from a CSV file named transactions.csv using the pandas library. 
It extracts the unique user IDs from the data.
"""
data = pd.read_csv('transactions.csv')
users = data['user_id'].unique()

"""
# === APPLICATION LAYOUT === #

The layout of the web application is defined using HTML and Dash components. It includes the following elements:
-	A container for the application content.
-	A row containing a title and a description.
-	A navigation bar with links to GitHub, settings, and FAQ pages.
-	Input fields for email and password.
-	A submit button for form submission.
-	A link to the selection page.
-	An alert message for providing additional information.
-	An image related to fraud detection (for aesthetic purposes)
"""
app1.layout = html.Div([
    dbc.Container([
        dbc.Row([
                   html.H1(["Welcome to DetectiveFraud"]),
                   html.H2(["Keep your transactions safe from thieves!"
                ]),
                   html.P('', style={'margin-bottom': '20px'}),]),
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
            ]),
               html.P('', style={'margin-bottom': '20px'}),
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

"""
# === CALLBACK FUNCTION AND FLASK ROUTE === #
The code then defines a callback function using the app1.callback decorator. 
The callback function is triggered by changes in the email input field. 
It checks if the entered email ends with "@gmail.com" and updates the validity state of the email input field accordingly.
""""
@app1.callback(
    [Output("email-input", "valid"), Output("email-input", "invalid")],
    [Input("email-input", "value")],
)
def check_validity(text):
    if text:
        is_gmail = text.endswith("@gmail.com")
        return is_gmail, not is_gmail
    return False, False
"""
The code defines a Flask route for the homepage ("/") using the @app_flask1.route decorator. 
The route redirects to the root URL ("/").
"""

@app_flask1.route('/')
def homepage():
    return redirect('/')

"""
 # === EXECUTION === #
The code checks if the current module is being run as the main script by using the __name__ variable.
If it is the main script, the Flask application (app_flask1) is run in debug mode on port 5050 (it can be ommitted, but for persistency purposes, it is specified).
"""

if __name__ == "__main__":
    app_flask1.run(debug=True, port= 5050)
