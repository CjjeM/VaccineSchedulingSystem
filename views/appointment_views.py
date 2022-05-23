from flask import render_template, session, Flask, redirect, url_for, flash, request, jsonify
from flask.views import MethodView
from flask_login import login_required
from models.models import user_information, hospital, vaccine, availability_details, appointment
from models.forms import AddAppointmentForm
from web_app import db
import folium
from geopy.geocoders import Nominatim
import openrouteservice as ors
import json
from sqlalchemy import inspect
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta
from dateutil. relativedelta import relativedelta

app = Flask(__name__)


def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c

class ScheduleAppointmentView(MethodView):
    #decorators = [login_required]

    def form(self):
        return AddAppointmentForm()

    def get(self):
        low = self._render_map()[0]
        suggHosp = self._render_map()[1]
        hospital_data = self._get_hospital_data()
        json_data = json.dumps(hospital_data)
        return render_template("ScheduleAppointment.html", lowestdistance=low, form=self.form(), hospital_data=hospital_data, json_data=json_data, suggHosp=suggHosp)

    def _render_map(self):
        nom = Nominatim(user_agent="vac_system")
        hospno = hospital.query.count()
        lowestdist = 1000
        hospdist = 0
        lowestdisthospital = ""
        hospList = []
        listofSuggestedHosp = "| "
        c = 0

        try:
            current_user = user_information.query.filter_by(email_address=session["user"]).first()
        except:
            current_user = None
        if(current_user is None):
             current_geocode = nom.geocode("malayan colleges laguna")
        else:
            print(current_user.home_address)
            current_geocode = nom.geocode(current_user.home_address)
        
        user_latitude = current_geocode.latitude
        user_longitude = current_geocode.longitude

        for hoz in range(hospno):
            curhospital = hospital.query.filter_by(hosp_id=f'{hoz + 1}').first()
            hospital_geocode = nom.geocode(curhospital.hosp_name)
            hospital_latitude = hospital_geocode.latitude
            hospital_longitude = hospital_geocode.longitude

            hospdist = haversine(user_latitude, user_longitude, hospital_latitude, hospital_longitude)

            if hospdist < lowestdist:
                lowestdist = hospdist
                lowestdisthospital = curhospital.hosp_name
            else:
                lowestdist = lowestdist

            hospList.append([hospdist,curhospital.hosp_name])

        starthosp = hospital.query.filter_by(hosp_name=f'{lowestdisthospital}').first()
        starthosp_geocode = nom.geocode(starthosp.hosp_name)
        starthosp_latitude = starthosp_geocode.latitude
        starthosp_longitude = starthosp_geocode.longitude

        start_coords = (starthosp_latitude, starthosp_longitude)
        folium_map = folium.Map(
            location=start_coords,
            zoom_start=15
        )

        folium.Marker(
            [user_latitude, user_longitude], tooltip="Your Address",
            icon=folium.Icon(color='green', icon="fa-home", prefix='fa')
        ).add_to(folium_map)



        for h in range(hospno):
            currhospital = hospital.query.filter_by(hosp_id=f'{h + 1}').first()
            hospital1_geocode = nom.geocode(currhospital.hosp_name)
            hospital1_latitude = hospital1_geocode.latitude
            hospital1_longitude = hospital1_geocode.longitude

            vaxxcount = availability_details.query.filter_by(hosp_id=f'{h + 1}').count()
            available_vaccines = []
            available_dates = []
            available_time1 = []
            available_time2 = []
            vaccines = []

            try:
                for avail in range(vaxxcount):
                    curr_vax = availability_details.query.filter_by(id=f'{avail + 1}').first()
                    currdate = datetime.today()
                    curr_vax_availability = datetime.strptime(str(curr_vax.availability_date), '%Y-%m-%d')

                    if curr_vax_availability >= currdate:
                        available_vaccines.append(curr_vax.vac)
                        if curr_vax.availability_date.strftime("%m/%d/%Y") not in available_dates:
                            available_dates.append(curr_vax.availability_date.strftime("%m/%d/%Y"))

                        if curr_vax.availability_time1.strftime("%I:%M %p") not in available_time1:
                            available_time1.append(curr_vax.availability_time1.strftime("%I:%M %p"))

                        if curr_vax.availability_time2.strftime("%I:%M %p") not in available_time2:
                            available_time2.append(curr_vax.availability_time2.strftime("%I:%M %p"))
                            
                    else:
                        continue

                for v in available_vaccines:
                    vaxno = vaccine.query.filter_by(vaccine_id=f'{v}').first()
                    vaccines.append(vaxno.vaccine_name)
            except:
                vaccines.append("NO VACCINES AVAILABLE")
                available_dates.append("NO SCHEDULE DATES")
                available_time1.append("NO AVAILABLE")
                available_time2.append("TIMES")

            html = f'''
                        <b>{currhospital.hosp_name}</b><br>
                        <i>Available Vaccines and Dates:<br> 
                        {(", ".join(vaccines))}</i><br>
                        {(", ".join(available_dates))}<br>
                        {(", ".join(available_time1))}<br>
                        {(", ".join(available_time2))}<br>
                    '''

            iframe = folium.IFrame(html,
                                   width=600,
                                   height=100)

            popup = folium.Popup(iframe,
                                 max_width=1000)

            fg = folium.FeatureGroup(name="Hospitals")
            fg.add_child(folium.Marker(
                [hospital1_latitude, hospital1_longitude],
                popup=popup, tooltip=f"{currhospital.hosp_name}",
                icon=folium.Icon(color='red', icon="fa-hospital-o", prefix='fa', )
            ))

            folium_map.add_child(fg)
        folium_map.save('static/map.html')
        folium_map
        
        hospList.sort()

        for hav, hos in hospList:
            listofSuggestedHosp += hos + " | "
            c += 1

            if c == 3:
                break

        return (lowestdisthospital, listofSuggestedHosp)
    
    
    def _get_hospital_data(self):
        hospno = hospital.query.count()

        hospital_data = {}
        #loop count of hospitals
        for i in range(hospno):
            hospital_id = i + 1
            current_hospital = hospital.query.filter_by(hosp_id=hospital_id).first()

            availability = availability_details.query.filter_by(hosp_id=hospital_id).all()
            
            # vaccines = []
            # for avail in availability:
            #     current_vaccine = vaccine.query.filter_by(vaccine_id=avail.vac).first()
            #     vaccines.append(current_vaccine.vaccine_name)
            vaccines={}
            #loop for all schedules in all available hospitals
            for avail in availability:
                #vaccines.append(current_vaccine.vaccine_name)
                #get all vaccines from each hospital
                availability2 = availability_details.query.filter_by(vac=avail.vac).all()
                avail_dates = {}
                #loop to get schedule for single vaccine
                for avail2 in availability2:
                    current_vaccine = vaccine.query.filter_by(vaccine_id=avail2.vac).first()
                    avail_dates[datetime.strftime(avail.availability_date, '%Y-%m-%d')]=current_vaccine.vaccine_type,(avail.availability_time1).strftime("%H:%M:%S")
                #add to dictionary with vaccine as key and schedule and vaccine type as values
                vaccines[current_vaccine.vaccine_name]=avail_dates
                print(vaccines)
            # vaccines = list(set(vaccines))
            
            # avail_dates = []

            # for avail in availability:
            #     avail_dates.append(datetime.strftime(avail.availability_date, '%Y-%m-%d'))

            # vac_types = []

            # for avail in availability:
            #     current_vaccine = vaccine.query.filter_by(vaccine_id=avail.vac).first()
            #     vac_types.append(current_vaccine.vaccine_type)

            # hospital_data[current_hospital.hosp_name] = [current_hospital.hosp_address,
            #                                             vaccines,
            #                                             avail_dates,vac_types]
            hospital_data[current_hospital.hosp_name] = [current_hospital.hosp_address,
                                                         vaccines]
            print(hospital_data)                                             
            print(hospital_data["Calamba Doctors Hospital"][1])
            for i in hospital_data["Calamba Doctors Hospital"][1]:
                 print(i)
            print("get")
        return hospital_data
    

    def _send_sms(self, form_data):
        current_user = user_information.query.filter_by(email_address=session["user"]).first()
        user_contact = current_user.contact_number
        
        account_sid = os.environ["ACCOUNT_SID"]
        print(account_sid)
        auth_token = os.environ["AUTH_TOKEN"]
        print(auth_token)
        message = f"""Hello! Here are the details of your appointment:
        Hospital Name: {form_data.hospitalname.data}
        Hospital Address: {form_data.hospitaladdress.data}
        Available Vaccines: {form_data.availablevaccines.data}
        Expected Date of Vaccination: {form_data.vaccineschedule.data}"""
        twilio_client = Client(account_sid, auth_token)
        twilio_client.messages.create(
            to = user_contact,
            from_= "+19035609492",
            body = message
        )

    def _send_email(self, form_data):
        current_user = user_information.query.filter_by(email_address=session["user"]).first()
        user_email = current_user.email_address
        from_sender = os.environ["FROM_SENDER"]
        sendgrid_api = os.environ["SENDGRID_API"]
        content = f"""Hello! Here are the details of your appointment:
        Hospital Name: {form_data.hospitalname.data}
        Hospital Address: {form_data.hospitaladdress.data}
        Available Vaccines: {form_data.availablevaccines.data}
        Expected Date of Vaccination: {form_data.vaccineschedule.data}"""
        
        mail_message = Mail(from_email=from_sender,
               to_emails=user_email,
               subject="Your Vaccine Appointment Summary",
               plain_text_content=content)
        
        sg = SendGridAPIClient(sendgrid_api)
        response = sg.send(mail_message)

        print(response.status_code)


    def post(self):
        form = self.form()
        if form.validate_on_submit():
            availability_date=form.vaccineschedule.data

            availability = availability_details.query.filter_by(availability_date=availability_date).first()
            user = user_information.query.filter_by(email_address=session["user"]).first()
            
            doser = user.dose_count
            dose=form.vaccinetype.data

            date_1 = datetime.strptime(availability_date, '%Y-%m-%d')

            
           
            if(dose=="not booster"):
                end_date = date_1 + relativedelta(months=6)
                
                if(user.dose_count==2):
                     flash(f'You have exceeded the number of doses needed for this vaccine '+str(end_date.date()) , category = 'warning')
                else:
                    end_date = date_1 + timedelta(days=21)
                    doser=2
                    flash(f'You may get your next dose on '+str(end_date.date()) , category = 'success')
                    
                    end_date = date_1 + relativedelta(months=6)
                    booster=1
                    user.schedule = availability.id
                    user.dose_count = doser
                    user.booster_count = booster
                    user.next_shot = end_date.date()
                    db.session.commit()
                    flash(f'You may get your next dose on '+str(end_date.date()) , category = 'success')
                    flash(f'You have made an appointment' , category = 'success')
                    return redirect(url_for('ViewAppointment'))
            if(dose=="booster"):
                if(user.dose_count<=1):
                    flash(f'You are not elligible for booster' , category = 'warning')
                else:
                    end_date = date_1 + relativedelta(months=6)
                    booster=1
                    user.schedule = availability.id
                    user.dose_count = doser
                    user.booster_count = booster
                    user.next_shot = end_date.date()
                    db.session.commit()
                    flash(f'You may get your next dose on '+str(end_date.date()) , category = 'success')
                    flash(f'You have made an appointment' , category = 'success')
                    return redirect(url_for('ViewAppointment'))
            #self._send_sms(form)
            #self._send_email(form)

            #session["vacid"] = user.vaccine_id
            #session['hospid'] = user.hosp_id
            #session["schedid"] = 0
            
            
            
            
        return redirect(url_for('ScheduleAppointment'))


class ViewAppointmentView(MethodView):
    decorators = [login_required]

    def get(self):

        view = db.session.query(user_information, availability_details, hospital, vaccine)\
                         .select_from(user_information)\
                         .join(availability_details, availability_details.avail_id == user_information.schedule)\
                         .join(hospital, hospital.hosp_id == availability_details.hosp_id)\
                         .join(vaccine, vaccine.vaccine_id == availability_details.vaccine_id)\
                         .first()

        user = user_information.query.filter_by(email_address=session["user"]).first()
        appoint = appointment.query.filter_by(avail_id=user_information.schedule).first()
        
        results = db.session.query(user_information, appointment)\
            .join(appointment, appointment.user_id == user_information.user_id, isouter=True)\
                .first()

        print(session["user"])
        print(user.first_name)
        return render_template("ViewAppointment.html", user=user, appoint=appoint)
