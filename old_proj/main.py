from flask import Flask, redirect, url_for, render_template, request, session
from views.user_views import *

app = Flask(__name__)
app.secret_key = "change_to_random_string"

login_view = LoginView.as_view('Login')
app.add_url_rule('/Login', methods=['GET', 'POST'], view_func=login_view)

register_view = RegisterView.as_view('Register')
app.add_url_rule('/Register', methods=['GET', 'POST'], view_func=register_view)

@app.route ("/")
def Home():
    return render_template("Home.html", content="Test")

@app.route ("/ScheduleAppointment")
def ScheduleAppointment():
    return render_template("ScheduleAppointment.html", content="Test")

@app.route ("/ViewAppointment")
def ViewAppointment():
    return render_template("ViewAppointment.html", content="Test")

if __name__ == "__main__":
    app.run(debug=True)