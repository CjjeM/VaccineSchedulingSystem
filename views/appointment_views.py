from flask import render_template
from flask.views import MethodView

class ScheduleAppointmentView(MethodView):
    def get(self):
        return render_template("ScheduleAppointment.html")

class ViewAppointmentView(MethodView):
    def get(self):
        return render_template("ViewAppointment.html")
