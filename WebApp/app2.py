"""
# === OVERVIEW === #
This python file is a demo of a hypothetical User Portal that can be accessible thorugh the credentials submission (see app1.py).
# === LIBRARIES === #
In this case, in addition to redirect(), also render_template_string is imported.
render_template_string is a function from the flask.templating package. 
It is used to generate output from a string that is directly passed inside the function, rather than from a file in the templates folder.
"""

from flask import  Flask, redirect, render_template_string


"""
# === FLASK APPLICATION INITIALIZATION  === #
The code initializes a Flask application using the following steps:
-	An instance of the Flask application (app_flask2) is created.
"""


app_flask2 = Flask(__name__)


"""
# === FLASK ROUTE AND RENDERING TEMPLATE  === #
-	The code defines a Flask route ("/") using the @app_flask2.route decorator. When a user accesses the root URL ("/"), the associated function hello_user() is called.
-	The hello_user() function uses render_template_string to render an HTML template with the following content:
-	This HTML template displays a welcome message for the user and notifies them about existing issues that are expected to be fixed soon.
After rendering the template, the code includes a return redirect('/') statement. This line of code redirects the user to the root URL ("/").
"""



@app_flask2.route('/')
def hello_user():
    return render_template_string("""
    <h1> Welcome back, User! </h1>
    <h3> At the moment there are some issues, we hope to fix them soon! </h3>
    """)
    return redirect('/')

"""
# === MAIN EXECUTION  === #
The code includes a conditional statement if __name__ =='__main__': to ensure that the Flask application is run only if the current module is being executed as the main script.
Inside this conditional block, the Flask application (app_flask2) is run using the run() method. The application runs in debug mode, enabling detailed error messages, and listens on port 1111.
"""

if __name__ =='__main__':
    app_flask2.run(debug=True, port = 1111)
