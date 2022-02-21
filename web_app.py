from flask import Flask, session, render_template
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import folium

user = "vaccinedb"
pwd = "vaccine"
host = "localhost"
database = "vaccinedb"

conn = f"mysql+pymysql://{user}:{pwd}@{host}/{database}"

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI']=conn
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"

db = SQLAlchemy(app)

ses = Session(app)

login_manager = LoginManager(app)
login_manager.login_view = "adminlogin"
login_manager.login_message_category = "info"

@app.route('/')
def index():
    start_coords = (14.3141, 121.1134)
    folium_map = folium.Map(
        location=start_coords,
        zoom_start=17
    )
    folium_map.save('templates/map.html')
    return render_template('Home.html')

@app.route('/map')
def map():
    return render_template('map.html')

from views.user_views import RegisterView, UserLoginView, LogoutView
from views.home_view import HomeView
from views.appointment_views import ScheduleAppointmentView, ViewAppointmentView
from views.admin_views import AdminLoginView,AddVaccineView,UpdateVaccineView,IndexView

home_view = HomeView.as_view('Home')
app.add_url_rule('/', methods=['GET'], view_func=home_view)

register_view = RegisterView.as_view('Register')
app.add_url_rule('/Register', methods=['GET', 'POST'], view_func=register_view)

login_view = UserLoginView.as_view('Login')
app.add_url_rule('/Login', methods=['GET', 'POST'], view_func=login_view)

logout_view = LogoutView.as_view('Logout')
app.add_url_rule('/Logout', methods=['GET', 'POST'], view_func=logout_view)

schedule_appointment_view = ScheduleAppointmentView.as_view('ScheduleAppointment')
app.add_url_rule('/ScheduleAppointment', methods=['GET', 'POST'], view_func=schedule_appointment_view)

view_appointment_view = ViewAppointmentView.as_view('ViewAppointment')
app.add_url_rule('/ViewAppointment', methods=['GET', 'POST'], view_func=view_appointment_view)

index_view = IndexView.as_view('index')
app.add_url_rule('/index', methods=['GET', 'POST'], view_func=register_view)

adminlogin_view = AdminLoginView.as_view('adminlogin')
app.add_url_rule('/adminlogin', methods=['GET', 'POST'], view_func=register_view)

updatevaccine_view = UpdateVaccineView.as_view('updatevaccine')
app.add_url_rule('/updatevaccine', methods=['GET', 'POST'], view_func=updatevaccine_view)

addvaccine_view = AddVaccineView.as_view('addvaccine')
app.add_url_rule('/addvaccine', methods=['GET', 'POST'], view_func=addvaccine_view)