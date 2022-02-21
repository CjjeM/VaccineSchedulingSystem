from web_app import db, login_manager,session
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    if session['account_type'] == 'Admin':
        return hospital.query.get(int(user_id))
    elif session['account_type'] == 'User':
        return user_information.query.get(int(user_id))
    else:
        session['account_type'] = None
        return None
    
class user_information(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(length=45))
    middle_name=db.Column(db.String(length=45))
    last_name=db.Column(db.String(length=45))
    city=db.Column(db.String(length=45))
    home_address=db.Column(db.String(length=45))
    birthdate=db.Column(db.Date)
    contact_number=db.Column(db.String(length=45))
    email_address=db.Column(db.String(length=45))
    pwd=db.Column(db.String(length=45))
    schedule=db.Column(db.Integer)


    def __repr__(self):
        return "id: {0} | first name: {1} | middle name: {2} | last name: {3} | city: {4} | home address: {5} | email address: {6} | password: {7} | contact number: {8} | birth date: {9}".format(self.id,self.first_name,self.middle_name,self.last_name,self.city,self.home_address,self.email_address,self.pwd,self.contact_number,self.birthdate,)



class vaccine(db.Model):
    __tablename__="vaccine"
    vaccine_id=db.Column(db.Integer,primary_key=True)
    vaccine_name=db.Column(db.String(length=255))
    hos=db.Column(db.Integer,db.ForeignKey('hospital.id'))
    vaccine_expiration=db.Column(db.Date)
    vaccine_manufacturer=db.Column(db.String(length=255))
    vaccine_supplier=db.Column(db.String(length=255))
    vaccine_information=db.Column(db.String(length=255))
    def __repr__(self):
        return f'<User: {self.vaccine_name}>'

class hospital(db.Model, UserMixin):
    __tablename__="hospital"
    id=db.Column(db.Integer,primary_key=True)
    hosp_name=db.Column(db.String(length=45))
    hosp_address=db.Column(db.String(length=255))
    sched = db.relationship('avail', backref='hospital', lazy=True)
    vac = db.relationship('vaccine', backref='hospital', lazy=True)
    def __repr__(self):
        return f'<User: {self.hosp_name}>'
    

class avail(db.Model):
    schedule_id=db.Column(db.Integer,primary_key=True)
    availability_date=db.Column(db.Date)
    availability_time1=db.Column(db.Time)
    availability_time2=db.Column(db.Time)
    vac=db.Column(db.Integer,db.ForeignKey('vaccine.vaccine_id'))
    hos=db.Column(db.Integer,db.ForeignKey('hospital.id'))
    