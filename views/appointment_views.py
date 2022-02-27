from flask import render_template, session, url_for, redirect, Flask
from flask.views import MethodView
from flask_login import login_required
from models.models import user_information, hospital, vaccine, availability_details
import folium
from geopy.geocoders import Nominatim
import openrouteservice as ors
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

    def get(self):
        self._render_map()
        return render_template("ScheduleAppointment.html")
    
    def post(self):
        self._send_sms()
        self._send_email()
        #return redirect(url_for("ViewAppointment"))
        low = self._render_map()
        return render_template("ScheduleAppointment.html", lowestdistance=low)

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

            vaxxcount = availability_details.query.count()
            available_vaccines = []
            available_dates = []
            available_time1 = []
            available_time2 = []
            vaccines = []


            try:
                for avail in range(vaxxcount):
                    curr_vax = availability_details.query.filter_by(id=f'{avail + 1}').first()
                    currdate = datetime.today().strftime('%Y-%m-%d')


                    if str(curr_vax.availability_date) == str(currdate):
                        if curr_vax.hos == h + 1:
                            available_vaccines += [curr_vax.vac]
                            if curr_vax.availability_date.strftime("%m/%d/%Y") not in available_dates:
                                available_dates += [curr_vax.availability_date.strftime("%m/%d/%Y")]

                            if curr_vax.availability_time1.strftime("%I:%M %p") not in available_time1:
                                available_time1 += [curr_vax.availability_time1.strftime("%I:%M %p")]

                            if curr_vax.availability_time2.strftime("%I:%M %p") not in available_time2:
                                available_time2 += [curr_vax.availability_time2.strftime("%I:%M %p")]

                        else:
                            continue

                    else:
                        continue

                for v in available_vaccines:
                    vaxno = vaccine.query.filter_by(vaccine_id=f'{v}').first()
                    vaccines += [vaxno.vaccine_name]
            except:
                vaccines += "NO VACCINES AVAILABLE"
                available_dates += "NO SCHEDULE DATES"
                available_time1 += "NO AVAILABLE"
                available_time2 += "TIMES"

            html = f'''
                        <b>{currhospital.hosp_name}</b><br>
                        <i>Available Vaccines and Dates:<br> 
                        {(', '.join(vaccines))}</i><br>
                        {(', '.join(available_dates))}<br>
                        {(', '.join(available_time1))}<br>
                        {(', '.join(available_time2))}<br>

                        <form action="/my-link/">
                        <input type="submit" value="Select" />
                        </form>

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
    
    def _send_sms(self):
        current_user = user_information.query.filter_by(email_address=session["user"]).first()
        user_contact = current_user.contact_number
        
        account_sid = os.environ["ACCOUNT_SID"]
        auth_token = os.environ["AUTH_TOKEN"]

        message = f"""Hello! Here are the details of your appointment:
        Hospital Name: 
        Hospital Address: 
        Available Vaccines: 
        Expected Date of Vaccination: """

        twilio_client = Client(account_sid, auth_token)
        twilio_client.messages.create(
            to = user_contact,
            from_= "+19035609492",
            body = message
        )


    def _send_email(self):
        current_user = user_information.query.filter_by(email_address=session["user"]).first()
        user_email = current_user.email_address
        from_sender = os.environ["FROM_SENDER"]
        sendgrid_api = os.environ["SENDGRID_API"]

        content = f"""Hello! Here are the details of your appointment:
        Hospital Name: 
        Hospital Address: 
        Available Vaccines: 
        Expected Date of Vaccination: """
        
        mail_message = Mail(from_email=from_sender,
               to_emails=user_email,
               subject="Your Vaccine Appointment Summary",
               plain_text_content="This is a test content2")
        
        sg = SendGridAPIClient(sendgrid_api)
        response = sg.send(mail_message)


class ViewAppointmentView(MethodView):
    decorators = [login_required]
    def get(self):
        return render_template("ViewAppointment.html")
