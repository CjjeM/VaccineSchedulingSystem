from flask import render_template, session, redirect, url_for, flash,request,Response
from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask.views import MethodView
from models.forms import AdminLoginForm,UpdateVaccineForm,AddVaccineForm,AdminLoginForm,UpdateItemForm
from models.models import hospital,vaccine,availability_details,user_information
from web_app import db
import io
import xlwt
import pymysql
from datetime import datetime, timedelta

class AdminLoginView(MethodView):
    
    def form(self):
        return AdminLoginForm()

    def get(self):
        return render_template('login_admin.html',form=self.form())
    
    def post(self):
        try:
            
            form = AdminLoginForm()
            session["account_type"] = None
            
            if form.validate_on_submit():
                
                attempted_user = hospital.query.filter_by(hosp_name=form.hosname.data).filter_by(hosp_id=form.hosid.data).first()
                if attempted_user:
                    session["account_type"] ="Admin"
                    session["user"] =form.hosname.data
                    session["hosid"] =form.hosid.data
                    login_user(attempted_user)
                    flash(f'Success! You are logged in as: {attempted_user.hosp_name}', category='success')
                    return redirect(url_for('vaccines'))
                else:
                    flash('Incorrect Hospital Name or Password, Try Again', category='danger')

            if form.errors != {}: 
                flash('Incorrect Hospital Name or Password, Try Again', category='danger')
        except:
            flash('Incorrect Name or Password, Try Again', category='danger')
        return redirect(url_for('adminlogin'))

class VaccinesView(MethodView):
    decorators = [login_required]
    def form(self):
        return UpdateItemForm()

    def get(self):
        s=[]
        items3= vaccine.query.filter_by(hosp_id=session["hosid"]).all()
        for i in items3:
            if i is None:
                continue
            
            else:
            
                s.append(i)
        
        return render_template('admin_index.html',form=self.form(),s=s)
    
    def post(self):
        form = self.form()
        if form.validate_on_submit()  and form.submit.data:
            print(request.form.get('current_vaccine'))
            session["vacid"] =request.form.get('current_vaccine')
            session["schedid"] =0
            items1 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
            flash(f'Editing Vaccine: {items1.vaccine_name}', category='success')
            return redirect(url_for('updatevaccine'))
    
        elif form.validate_on_submit() and form.delete.data:
            session["vacid"] =request.form.get('delete_vaccine')
            items3 =  availability_details.query.filter_by(vaccine_id=session["vacid"]).all()
            for i in items3:
                db.session.delete(i)
                db.session.commit()
            items2 =  vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
            db.session.delete(items2)
            db.session.commit()
            flash(f'Successfully Deleted Vaccine: {items2.vaccine_name}', category='success')
            return redirect(url_for('vaccines'))

class UpdateVaccineView(MethodView):
    def form(self):
        items2 =  availability_details.query.filter_by(avail_id=session["schedid"]).first()
        if items2 is None:
            man=""
        else:
            man=items2.availability_date
        return UpdateVaccineForm(vaccinedate=man)

    def get(self):
        s=[]
        u=[]
        
        users =  user_information.query.filter_by(schedule=session["schedid"]).all()
        items =  hospital.query.filter_by(hosp_id=session["hosid"]).first()
        items1 = vaccine.query.filter_by(vaccine_id=session["vacid"]).first()
        items3= availability_details.query.filter_by(hosp_id=session["hosid"]).filter_by(vaccine_id=session["vacid"]).all()

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
        print(u)
        return render_template('update.html',form=self.form(),s=s,items=items,items1=items1,u=u)
    
    def post(self):
        form = self.form()
        currdate = datetime.today()
        currdate=currdate.date()
        try:
            if  form.deletesched.data: 
                session["schedid"] =request.form.get('delete_schedule')
                items2 =  availability_details.query.filter_by(avail_id=session["schedid"]).filter_by(vaccine_id=session["vacid"]).filter_by(hosp_id=session["hosid"]).first()
                print(items2)
                db.session.delete(items2)
                db.session.commit()
                flash(f'Deleted Schedule Successfully', category='success')
                return redirect(url_for('updatevaccine'))

            if form.validate_on_submit() and form.addtime.data:
                

                items2 =  availability_details.query.filter_by(avail_id=session["schedid"]).filter_by(vaccine_id=session["vacid"]).filter_by(hosp_id=session["hosid"]).first()
                if form.vaccinedate.data >= currdate:
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
                else:
                    flash(f'Error! Entered date must be more than current date', category='danger')

            if  form.validate_on_submit() and form.add.data:
                if form.vaccinedate.data >= currdate:
                    user=availability_details(availability_date=form.vaccinedate.data,availability_time1=form.time1.data,availability_time2=form.time2.data,vaccine_id=session["vacid"],hosp_id=session["hosid"])
                    db.session.add(user)
                    db.session.commit()
                    flash(f'Updated Schedule Successfully', category='success')
                    return redirect(url_for('updatevaccine'))
                else:
                    flash(f'Error! Entered date must be more than current date', category='danger')
            
            if form.validate_on_submit()  and form.update.data:
                print(request.form.get('update_schedule'))
                items2 =  availability_details.query.filter_by(avail_id=request.form.get('update_schedule')).first()
                session["schedid"] =request.form.get('update_schedule')
                print(request.form.get('update_schedule'))
                flash(f'Now editing schedule with date: {items2.availability_date}', category='success')
                return redirect(url_for('updatevaccine'))
            else:
                flash(f'Invalid values', category='danger')
        except:
            flash(f'Invalid values', category='danger')
        return redirect(url_for('updatevaccine'))
class AddVaccineView(MethodView):
    def form(self):
        return AddVaccineForm()

    def get(self):
        return render_template('add.html',form=self.form())
    
    def post(self):
        form = self.form()
        currdate = datetime.today()
        currdate=currdate.date()
        #=datetime.strftime(form.expiration.data, '%Y-%m-%d')
        if form.validate_on_submit() and form.add.data:
                if form.expiration.data >= currdate:
                    user=vaccine(vaccine_name=form.vaccinename.data,hosp_id=session["hosid"],vaccine_expiration=form.expiration.data,vaccine_manufacturer=form.manufacturer.data
                    ,vaccine_supplier=form.supplier.data,vaccine_information=form.information.data,vaccine_type=form.vaccinetype.data)
                
                    db.session.add(user)
                    db.session.commit()
                    session["vacid"]=user.vaccine_id
                    session["schedid"]=0
                    flash(f'Success! You have added: {user.vaccine_name}', category='success')
                    flash(f'Add schedule to finish', category='success')
                    return redirect(url_for('updatevaccine'))
                else:
                    flash(f'Error! Entered date must be more than current date', category='danger')
        if form.errors != {}: 
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a vaccine: {err_msg}', category='danger')
        return redirect(url_for('addvaccine'))

class GenerateReportView(MethodView):
    def form(self):
        return GenerateReportView()

    def get(self):
        conn = None
        cursor = None
    
        items1 = vaccine.query.filter_by(hosp_id=session["hosid"])
        
        output = io.BytesIO()
        workbook = xlwt.Workbook()
        #add a sheet
        sh = workbook.add_sheet('Vaccine Report')
        
        #add headers
        sh.write(0, 0, 'Vaccine ID')
        sh.write(0, 1, 'Vaccine Name')
        sh.write(0, 2, 'Hospital')
        sh.write(0, 3, 'Vaccine Manufacturer')
        sh.write(0, 4, 'Vaccine Supplier')
        sh.write(0, 5, 'Vaccine Information')
        
        idx = 0
        for row in items1:
            print(row.vaccine_id)
            sh.write(idx+1, 0, row.vaccine_id)
            sh.write(idx+1, 1, row.vaccine_name)
            sh.write(idx+1, 2, row.hosp_id)
            sh.write(idx+1, 3, row.vaccine_manufacturer)
            sh.write(idx+1, 4, row.vaccine_supplier)
            sh.write(idx+1, 5, row.vaccine_information)
            idx += 1
        
        workbook.save(output)
        output.seek(0)
        
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=vaccine_report.xls"})
    
    