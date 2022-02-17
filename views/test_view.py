from flask import render_template
from flask.views import MethodView

class TestView(MethodView):
    def get(self):
        return render_template("Login.html", content="Test")

    def post(self):
        pass