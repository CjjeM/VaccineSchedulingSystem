from flask import render_template, session, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from models.forms import RegisterForm, LoginForm
from models.models import user_information
from web_app import db


class UserLoginView(MethodView):
    def form(self):
        return LoginForm()

    def get(self):
        return render_template('login.html',form=self.form())

    def post(self):
        user_form = LoginForm()

        if user_form.validate_on_submit() or user_form.errors != {}:
            email = user_form.emailadd.data
            password = user_form.password.data
            
            attempted_user = user_information.query.filter_by(email_address=email).first()

            if attempted_user:
                password_passed = check_password_hash(attempted_user.pwd, password)
                if password_passed:
                    session["account_type"] ="User"
                    session["user"] = user_form.emailadd.data
                    login_user(attempted_user)
                    flash(f'Success! You are logged in as: {attempted_user.email_address}', category='success')
                    return redirect(url_for('ViewAppointment'))

            flash('Incorrect Email or Password, Try Again', category='danger')
        
        return render_template('login.html',form=user_form)
        

class RegisterView(MethodView):
    def form(self):
        return RegisterForm()

    def get(self):
        return render_template('register.html',form=self.form())

    def post(self):
        register_form = self.form()
        if register_form.validate_on_submit():
            password = register_form.password.data
            hashed_password = generate_password_hash(password)

            user = user_information(first_name=register_form.first_name.data,
                                    middle_name=register_form.middle_name.data,
                                    last_name=register_form.last_name.data,
                                    city=register_form.city.data,
                                    home_address=register_form.home_address.data,
                                    email_address=register_form.email_address.data,
                                    pwd=hashed_password,
                                    contact_number=register_form.contact_number.data,
                                    birthdate=register_form.birthdate.data,
                                    schedule=1)

            db.session.add(user)
            db.session.commit()
        
            flash(f'Success! You are registered', category='success')
            
        if register_form.errors != {}: 
            for err_msg in register_form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')
        
        return render_template('register.html',form=register_form)

class LogoutView(MethodView):
    def get(self):
        logout_user()
        flash("You have been logged out!", category='info')
        return redirect(url_for("Login"))
    
    def post(self):
        logout_user()
        flash("You have been logged out!", category='info')
        return redirect(url_for("Login"))