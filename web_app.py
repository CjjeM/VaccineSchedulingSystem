from flask import Flask, session
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

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

from views.user_views import RegisterView, UserLoginView
from views.home_view import HomeView
from views.appointment_views import ScheduleAppointmentView, ViewAppointmentView

register_view = RegisterView.as_view('Register')
app.add_url_rule('/Register', methods=['GET', 'POST'], view_func=register_view)

home_view = HomeView.as_view('Home')
app.add_url_rule('/', methods=['GET'], view_func=home_view)

login_view = UserLoginView.as_view('Login')
app.add_url_rule('/Login', methods=['GET', 'POST'], view_func=login_view)

schedule_appointment_view = ScheduleAppointmentView.as_view('ScheduleAppointment')
app.add_url_rule('/ScheduleAppointment', methods=['GET', 'POST'], view_func=schedule_appointment_view)

view_appointment_view = ViewAppointmentView.as_view('ViewAppointment')
app.add_url_rule('/ViewAppointment', methods=['GET', 'POST'], view_func=view_appointment_view)
