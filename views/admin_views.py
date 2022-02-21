from flask import render_template, session, redirect, url_for, flash,request
from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from models.forms import AdminLoginForm,UpdateVaccineForm,AddVaccineForm,AdminLoginForm,UpdateItemForm
from models.models import hospital,vaccine,avail,user_information
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

class IndexView(MethodView):
    decorators = [login_required]
    def form(self):
        return UpdateItemForm()

    def get(self):
        s=[]
        session["schedid"] =0
        items3= vaccine.query.filter_by(hos=session["hosid"]).all()
        for i in items3:
            if i is None:
                continue
            
            else:
            
                s.append(i)
        
        return render_template('login_admin.html',form=self.form(),s=s)
    
    def post(self):
        form = self.form()
        if form.validate_on_submit()  and form.submit.data:
            print(request.form.get('current_vaccine'))
            session["vacid"] =form.form.get('current_vaccine')
            items1 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
            flash(f'Editing Vaccine: {items1.vaccine_name}', category='success')
            return redirect(url_for('updatevaccine'))
    
        elif form.validate_on_submit() and form.delete.data:
            session["vacid"] =request.form.get('delete_vaccine')
            items3 =  avail.query.filter_by(vac=session["vacid"]).all()
            for i in items3:
                db.session.delete(i)
                db.session.commit()
            items2 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
            db.session.delete(items2)
            db.session.commit()

class UpdateVaccineView(MethodView):
    def form(self):
        items2 =  avail.query.filter_by(schedule_id=session["schedid"]).first()
        if items2 is None:
            man=""
        else:
            man=items2.availability_date
        return UpdateVaccineForm(vaccinedate=man)

    def get(self):
        s=[]
        u=[]
        users =  user_information.query.filter_by(schedule=session["schedid"]).all()
        items =  hospital.query.filter_by(id=session["hosid"]).first()
        items1 = vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
        items3= avail.query.filter_by(hos=session["hosid"]).filter_by(vac=session["vacid"]).all()

        for i in items3:
            if i is None:
                continue
            else:
                s.append(i)

        if users is None:
            u=[]
        else:
            for i in users:
                if i is None:
                    continue
                else:
                    u.append(i)
        return render_template('login_admin.html',form=self.form(),s=s,items=items,items1=items1)
    
    def post(self):
        form = self.form()
        if  form.deletesched.data: 
            print(request.form.get('delete_schedule'))
            session["schedid"] =request.form.get('delete_schedule')
            items2 =  avail.query.filter_by(schedule_id=session["schedid"]).filter_by(vac=session["vacid"]).filter_by(hos=session["hosid"]).first()
            print(items2)
            db.session.delete(items2)
            db.session.commit()
            flash(f'Deleted Schedule Successfully', category='success')
            return redirect(url_for('updatevaccine'))

        if form.validate_on_submit() and form.addtime.data:
            print(session["schedid"])
            items2 =  avail.query.filter_by(schedule_id=session["schedid"]).filter_by(vac=session["vacid"]).filter_by(hos=session["hosid"]).first()
            if items2 is None:
                flash(f'No schedule selected', category='danger')
            else:
                items2.availability_date=form.vaccinedate.data
                db.session.commit()
                items2.availability_time1=form.time1.data
                db.session.commit()
                items2.availability_time2=form.time2.data
                db.session.commit()
                flash(f'Updated Schedule Successfully', category='success')
                return redirect(url_for('updatevaccine'))

        if  form.add.data:
            user=avail(availability_date=form.vaccinedate.data,availability_time1=form.time1.data,availability_time2=form.time2.data,vac=session["vacid"],hos=session["hosid"])
            db.session.add(user)
            db.session.commit()
            flash(f'Updated Schedule Successfully', category='success')
            return redirect(url_for('updatevaccine'))
        
        if form.validate_on_submit()  and form.update.data:
            today = form.today()
            print(today)
            items2 =  avail.query.filter_by(schedule_id=request.form.get('update_schedule')).first()
            session["schedid"] =request.form.get('update_schedule')
            print(request.form.get('update_schedule'))
            flash(f'Now editing schedule with date: {items2.availability_date}', category='success')
            return redirect(url_for('updatevaccine'))

class AddVaccineView(MethodView):
    def form(self):
        return AddVaccineForm()

    def get(self):
        return render_template('login_admin.html',form=self.form())
    
    def post(self):
        form = self.form()
        if form.validate_on_submit() and form.add.data:
            user=vaccine(vaccine_name=form.vaccinename.data,hos=session["hosid"],vaccine_expiration=form.expiration.data,vaccine_manufacturer=form.manufacturer.data
            ,vaccine_supplier=form.supplier.data,vaccine_information=form.information.data)
        
            db.session.add(user)
            db.session.commit()
            session["vacid"]=user.vaccine_id
            flash(f'Success! You have added: {user.vaccine_name}', category='success')
            flash(f'Add schedule to finish', category='success')
            return redirect(url_for('updatevaccine'))
    if form.errors != {}: 
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')