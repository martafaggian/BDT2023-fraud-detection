from flask import  Flask, redirect, render_template_string


app_flask2 = Flask(__name__)

@app_flask2.route('/')
def hello_user():
    return render_template_string("""
    <h1> Welcome back, User! </h1>
    <h3> At the moment there are some issues, we hope to fix them soon! </h3>
    """)
    return redirect('/')

if __name__ =='__main__':
    app_flask2.run(host="0.0.0.0", debug=True, port = 1111)
