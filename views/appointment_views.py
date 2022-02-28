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

from math import radians, cos, sin, asin, sqrt
from datetime import date, datetime


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
    decorators = [login_required]

    def form(self):
        return AddAppointmentForm()

    def get(self):
        low = self._render_map()
        print(low)
        hospital_data = self._get_hospital_data()
        json_data = json.dumps(hospital_data)
        return render_template("ScheduleAppointment.html", lowestdistance=low, form=self.form(), hospital_data=hospital_data, json_data=json_data)

    def _render_map(self):
        nom = Nominatim(user_agent="vac_system")
        hospno = hospital.query.count()
        lowestdist = 1000
        hospdist = 0
        lowestdisthospital = ""

        current_user = user_information.query.filter_by(email_address=session["user"]).first()
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

            vaxxcount = availability_details.query.filter_by(hos=f'{h + 1}').count()
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
        return lowestdisthospital
    
    def _get_hospital_data(self):
        hospno = hospital.query.count()

        hospital_data = {}

        for i in range(hospno):
            hospital_id = i + 1
            current_hospital = hospital.query.filter_by(hosp_id=hospital_id).first()

            availability = availability_details.query.filter_by(hos=hospital_id).all()
            vaccines = []

            for avail in availability:
                current_vaccine = vaccine.query.filter_by(vaccine_id=avail.vac).first()
                vaccines.append(current_vaccine.vaccine_name)
                
            vaccines = list(set(vaccines))

            avail_dates = []

            for avail in availability:
                avail_dates.append(datetime.strftime(avail.availability_date, '%Y-%m-%d'))

            hospital_data[current_hospital.hosp_name] = [current_hospital.hosp_address,
                                                        vaccines,
                                                        avail_dates]

        return hospital_data


    def post(self):
        form = self.form()
        if form.validate_on_submit() and form.schedule.data:
            
            vac1=vaccine.query.filter_by(vaccine_name=form.availablevaccines.data).first()
            hos1=hospital.query.filter_by(hosp_name=form.hospitalname.data).first()
            hos2=hos1.hosp_id
            scheds=availability_details.query.filter_by(availability_date=form.vaccineschedule.data).filter_by(hos=hos2).filter_by(vac=vac1.vaccine_id).first()
            us=user_information.query.filter_by(email_address=session["user"]).first()
            us.schedule=scheds.id
            db.session.commit()
            flash(f'You have made an appointment' , category = 'success')
            return redirect(url_for('ViewAppointment'))

        return redirect(url_for('ScheduleAppointment'))


class ViewAppointmentView(MethodView):
    decorators = [login_required]

    def get(self):

       view = vaccine.query\
        .join(hospital, hospital.hosp_id == vaccine.vaccine_id) \
        .add_columns(vaccine.vaccine_id, vaccine.vaccine_name,vaccine.hos, hospital.hosp_id,hospital.hosp_name,hospital.hosp_id) \
        .join(availability_details, availability_details.vac == vaccine.vaccine_id)\
        .add_columns(appointment.id, appointment.user_id,appointment.availability_id, availability_details.hos,availability_details.availability_date,availability_details.availability_time1,availability_details.vac) \
        .join(appointment, appointment.availability_id == availability_details.id) \
        .add_columns(user_information.user_id,user_information.first_name,user_information.middle_name,user_information.last_name,user_information.email_address) \
        .filter(user_information.email_address == session["user"]).first()

       return render_template("ViewAppointment.html", view=view)
