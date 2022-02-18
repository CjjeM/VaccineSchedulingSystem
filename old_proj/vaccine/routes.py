from vaccine import app, db,login_manager,ses
from flask import Flask, render_template,redirect, url_for, flash, request,session
from flask_sqlalchemy import SQLAlchemy
from vaccine.models import user_information,hospital,vaccine,avail
from flask_login import current_user,login_user, logout_user, login_required 
from vaccine.forms import RegisterForm,LoginForm, UpdateVaccineForm, AddSchedForm,AddVaccineForm,AdminLoginForm,UpdateItemForm,DeleteItemForm,UpdateSchedForm,DeleteSchedForm
from wtforms.validators import ValidationError
from datetime import datetime, date, timedelta,time


@app.route ("/")
def Home():
    return render_template("Home.html", content="Test")

@app.route ("/ScheduleAppointment")
def ScheduleAppointment():
    return render_template("ScheduleAppointment.html", content="Test")

@app.route ("/ViewAppointment")
def ViewAppointment():
    return render_template("ViewAppointment.html", content="Test")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        
        attempted_user = user_information.query.filter_by(email_address=form.emailadd.data).first()
        if attempted_user:
            session["account_type"] ="User"
            session["user"] =form.emailadd.data
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.email_address}', category='success')
            return redirect(url_for('ViewAppointment'))
        else:
            print("shes1")
            flash('Incorrect Email or Passowrd, Try Again', category='danger')
    if form.errors != {}: 
        flash('Incorrect Email or Passowrd, Try Again', category='danger')

    return render_template('login.html',form=form)

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    form = AdminLoginForm()
    session["account_type"] =None
    
    if form.validate_on_submit():
        
        attempted_user = hospital.query.filter_by(hosp_name=form.hosname.data).filter_by(id=form.hosid.data).first()
        if attempted_user:
            session["account_type"] ="Admin"
            session["user"] =form.hosname.data
            session["hosid"] =attempted_user.id
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.hosp_name}', category='success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect Credentials, Try Again', category='danger')

    if form.errors != {}: 
        flash('Incorrect Name or Password, Try Again', category='danger')
    return render_template('login_admin.html',form=form)

@app.route('/update', methods=['GET', 'POST'])
@login_required
def index():
    s=[]
    session["schedid"] =0
    form1 = UpdateItemForm()
    form2 = DeleteItemForm()
    items =  hospital.query.filter_by(hosp_name=session["user"]).first()
    items3= vaccine.query.filter_by(hos=session["hosid"]).all()
    if form1.validate_on_submit()  and form1.submit.data:
        print(request.form.get('current_vaccine'))
        session["vacid"] =request.form.get('current_vaccine')
        items1 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
        flash(f'Editing Vaccine: {items1.vaccine_name}', category='success')
        return redirect(url_for('updatevaccine'))
    
    elif form2.validate_on_submit() and form2.delete.data:
        session["vacid"] =request.form.get('delete_vaccine')
        items3 =  avail.query.filter_by(vac=session["vacid"]).all()
        for i in items3:
            db.session.delete(i)
            db.session.commit()
        items2 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
        db.session.delete(items2)
        db.session.commit()
        
        flash(f'Deleted Vaccine: {items2.vaccine_name}', category='success')
        return redirect(url_for('index'))
        
    for i in items3:
        if i is None:
            continue
        
        else:
           
            s.append(i)
    
    return render_template('index.html',s=s,form1=form1,form2=form2)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        
        user=user_information(first_name=form.first_name.data,middle_name=form.middle_name.data,last_name=form.last_name.data,
        city=form.city.data,home_address=form.home_address.data,email_address=form.email_address.data,pwd=form.password.data,
        contact_number=form.contact_number.data,birthdate=form.birthdate.data)
        db.session.add(user)
        db.session.commit()
    
        flash(f'Success! You are registered', category='success')
    if form.errors != {}: 
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html',form=form)

@app.route('/logout', methods=['GET','POST'])
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("login"))

@app.route('/updatevaccine', methods=['GET', 'POST'])
def updatevaccine():
    s=[]
    delsched = DeleteSchedForm()
    
    items2 =  avail.query.filter_by(schedule_id=session["schedid"]).first()
    if items2 is None:
        man=""
        start=""
        end=""
    else:
        man=items2.availability_date

    udsched=UpdateVaccineForm(vaccinedate=man)
    adsched = AddSchedForm()
    
    up=UpdateSchedForm()
    items =  hospital.query.filter_by(id=session["hosid"]).first()
    items1 = vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
    items3= avail.query.filter_by(hos=session["hosid"]).filter_by(vac=session["vacid"]).all()

    if delsched.validate_on_submit()  and delsched.deletesched.data: #working
        print(request.form.get('delete_schedule'))
        session["schedid"] =request.form.get('delete_schedule')
        items2 =  avail.query.filter_by(schedule_id=session["schedid"]).filter_by(vac=session["vacid"]).filter_by(hos=session["hosid"]).first()
        print(items2)
        db.session.delete(items2)
        db.session.commit()
        flash(f'Deleted Schedule Successfully', category='success')
        return redirect(url_for('updatevaccine'))

    if udsched.validate_on_submit() and udsched.addtime.data:
        print(session["schedid"])
        items2 =  avail.query.filter_by(schedule_id=session["schedid"]).filter_by(vac=session["vacid"]).filter_by(hos=session["hosid"]).first()
        if items2 is None:
            flash(f'No schedule selected', category='danger')
        else:
            items2.availability_date=udsched.vaccinedate.data
            db.session.commit()
            items2.availability_time1=udsched.time1.data
            db.session.commit()
            items2.availability_time2=udsched.time2.data
            db.session.commit()
            flash(f'Updated Schedule Successfully', category='success')
            return redirect(url_for('updatevaccine'))

    if adsched.validate_on_submit() and adsched.add.data:
        user=avail(availability_date=udsched.vaccinedate.data,availability_time1=udsched.time1.data,availability_time2=udsched.time2.data,vac=session["vacid"],hos=session["hosid"])
        db.session.add(user)
        db.session.commit()
        flash(f'Updated Schedule Successfully', category='success')
        return redirect(url_for('updatevaccine'))
    
    if up.validate_on_submit()  and up.update.data:
        today = date.today()
        print(today)
        items2 =  avail.query.filter_by(schedule_id=request.form.get('update_schedule')).first()
        session["schedid"] =request.form.get('update_schedule')
        print(request.form.get('update_schedule'))
        flash(f'Now editing schedule with date: {items2.availability_date}', category='success')
        return redirect(url_for('updatevaccine'))
    if udsched.errors != {}: 
        print(udsched.time2.data)
        for err_msg in udsched.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    for i in items3:
        if i is None:
            continue
        else:
            s.append(i)
     
    return render_template('update.html',items2=items2,adsched=adsched, udsched=udsched,s=s,delsched=delsched,items1=items1,items=items,up=up)

@app.route('/addvaccine', methods=['GET', 'POST'])
def addvaccine():
    adform = AddVaccineForm()
    if adform.validate_on_submit():
        user=vaccine(vaccine_name=adform.vaccinename.data,hos=session["hosid"])
        
        db.session.add(user)
        db.session.commit()
        session["vacid"]=user.vaccine_id
        flash(f'Success! You have added: {user.vaccine_name}', category='success')
        flash(f'Add schedule to finish', category='success')
        return redirect(url_for('updatevaccine'))
        
    return render_template('add.html', adform=adform)

if __name__ == "__main__":
    app.run(debug=True)
