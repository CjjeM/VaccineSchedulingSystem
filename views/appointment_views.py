from flask import render_template, session, url_for, redirect
from flask.views import MethodView
from flask_login import login_required
from models.models import user_information
import folium
from geopy.geocoders import Nominatim
import openrouteservice as ors
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class ScheduleAppointmentView(MethodView):
    decorators = [login_required]
    def get(self):
        self._render_map()
        return render_template("ScheduleAppointment.html")
    
    def post(self):
        self._send_sms()
        self._send_email()
        return redirect(url_for("ViewAppointment"))


    def _render_map(self):
        # REMINDER!!!
        # for folium or OpenStreetMap, use (latitude, longitude)
        # for OpenRouteService, use (longitude, latitude)

        nom = Nominatim(user_agent="vac_system")
        # get list then convert to geocode for hospitals

        current_user = user_information.query.filter_by(email_address=session["user"]).first()
        current_geocode = nom.geocode(current_user.home_address)
        user_latitude = current_geocode.latitude
        user_longitude = current_geocode.longitude

        hospital1 = "Calamba Doctors Hospital"
        hospital1_geocode = nom.geocode(hospital1)
        hospital1_latitude = hospital1_geocode.latitude
        hospital1_longitude = hospital1_geocode.longitude
        
        start_coords = (user_latitude, user_longitude)
        folium_map = folium.Map(
            location=start_coords,
            zoom_start=17
        )

        folium.Marker(
            [user_latitude, user_longitude]
        ).add_to(folium_map)

        folium.Marker(
            [hospital1_latitude, hospital1_longitude]
        ).add_to(folium_map)

        folium_map.save('static/map.html')
    
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
