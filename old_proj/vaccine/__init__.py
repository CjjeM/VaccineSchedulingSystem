from flask import Flask, render_template,redirect, url_for, flash, request,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format('root','123456','localhost' ,'vaccine_system')
from flask_session import Session

app=Flask(__name__)
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI']=conn
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
ses=Session(app)

db=SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "adminlogin"
login_manager.login_message_category = "info"

from vaccine import routes