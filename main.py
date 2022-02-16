from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.secret_key = "change_to_random_string"

@app.route ("/")
def Home():
    return render_template("Home.html", content="Test")

@app.route ("/ScheduleAppointment")
def ScheduleAppointment():
    return render_template("ScheduleAppointment.html", content="Test")

@app.route ("/ViewAppointment")
def ViewAppointment():
    return render_template("ViewAppointment.html", content="Test")

@app.route ("/Login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        # insert db method
        user = request.form["form"]
        session["user"] = user
        return redirect(url_for("/"))

    return render_template("Login.html", content="Test")

@app.route ("/Register")
def Register():
    return render_template("Register.html", content="Test")

if __name__ == "__main__":
    app.run(debug=True)