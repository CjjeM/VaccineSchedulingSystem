from flask import render_template, session, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from database.main_db import mysqldb

db = mysqldb()

class LoginView(MethodView):
    def get(self):
        return render_template("Login.html")

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        session["user"] = email
        return redirect(url_for("Home"))


class RegisterView(MethodView):
    """
    # check first if email exists
        email = request.form["email"]
        
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        
        session["user"] = email

        db.add_user(email, hashed_password)

    """
    def get(self):
        return render_template("Register.html")
    
    def post(self):
        pass
