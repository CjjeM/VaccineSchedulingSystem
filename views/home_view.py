from flask import render_template
from flask.views import MethodView

class HomeView(MethodView):
    def get(self):
        get_vaccinated = "https://user-images.githubusercontent.com/85144867/153392397-6e210bd8-8565-4d00-b508-18947596a46f.png"
        register_vaccine = "https://user-images.githubusercontent.com/85144867/153390214-c584c272-d09d-4606-b3d3-c25497352c67.jpg"
        vaccine_pic = "https://user-images.githubusercontent.com/85144867/153391039-f61eeec1-3c55-400a-8c99-65da7e50e290.jpg"
        what_are_covid_vaccines = "https://user-images.githubusercontent.com/85144867/153391445-feb7347a-0c5a-4234-a0aa-7c4d6deefad7.png"
        
        return render_template("Home.html", 
        get_vaccinated=get_vaccinated, 
        register_vaccine=register_vaccine,
        vaccine_pic=vaccine_pic,
        what_are_covid_vaccines=what_are_covid_vaccines)
