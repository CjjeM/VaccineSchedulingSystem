from flask import render_template, session, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from models.forms import RegisterForm, LoginForm, AdminLoginForm
from models.models import user_information
from web_app import db


class UserLoginView(MethodView): #incomplete
    def get(self):
        pass

    def post(self):
        pass


class RegisterView(MethodView):
    def form(self):
        return RegisterForm()

    def get(self):
        return render_template('register.html',form=self.form())

    def post(self):
        register_form = self.form()
        if register_form.validate_on_submit():
            
            user = user_information(first_name=register_form.first_name.data,
                                    middle_name=register_form.middle_name.data,
                                    last_name=register_form.last_name.data,
                                    city=register_form.city.data,
                                    home_address=register_form.home_address.data,
                                    email_address=register_form.email_address.data,
                                    pwd=register_form.password.data,
                                    contact_number=register_form.contact_number.data,
                                    birthdate=register_form.birthdate.data)

            db.session.add(user)
            db.session.commit()
        
            flash(f'Success! You are registered', category='success')
        if register_form.errors != {}: 
            for err_msg in register_form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')
        
        return render_template('register.html',form=register_form)