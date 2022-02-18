from flask import render_template, session, redirect, url_for, flash
from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from models.forms import AdminLoginForm
from models.models import hospital
from web_app import db

class AdminLoginView(MethodView):
    def form(self):
        return AdminLoginForm()

    def get(self):
        return render_template('login_admin.html',form=self.form())
    
    def post(self):
        form = self.form()
        session["account_type"] = None
        
        if form.validate_on_submit():
            
            attempted_user = hospital.query.filter_by(hosp_name=form.hosname.data).first()
            if attempted_user:
                session["account_type"] ="Admin"
                session["user"] =form.hosname.data
                session["hosid"] =attempted_user.id
                login_user(attempted_user)
                flash(f'Success! You are logged in as: {attempted_user.hosp_name}', category='success')
                return redirect(url_for('index'))

        if form.errors != {}: 
            flash('Incorrect Name or Password, Try Again', category='danger')


class UpdateVaccineView(MethodView):
    decorators = [login_required]
