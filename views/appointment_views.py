from flask import render_template, session
from flask.views import MethodView
from flask_login import login_required
from models.models import user_information
import folium
from geopy.geocoders import Nominatim
import openrouteservice as ors

class ScheduleAppointmentView(MethodView):
    decorators = [login_required]
    def get(self):
        self._render_map()
        return render_template("ScheduleAppointment.html")

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

class ViewAppointmentView(MethodView):
    decorators = [login_required]
    def get(self):
        return render_template("ViewAppointment.html")
