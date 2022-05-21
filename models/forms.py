from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,DateField,TimeField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models.models import user_information, availability_details, vaccine, hospital, appointment

cities = ['Alaminos', 'Bay', 'Biñan', 'Cabuyao','Calamba','Calauan','Cavinti','Famy','Kalayaan','Liliw',
    'Los Baños','Luisiana','Lumban','Mabitac','Magdalena','Majayjay','Nagcarlan','Paete','Pagsanjan','Pakil',
    'Pangil','Pila','Rizal','San Pablo','San Pedro','Santa Cruz','Santa Maria','Sta. Rosa','Siniloan','Victoria']


class RegisterForm(FlaskForm):

    def validate_email_address(self, email_address_to_check):
        email_address = user_information.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')
    
    first_name = StringField(label='First Name:',validators=[DataRequired()])
    middle_name = StringField(label='Middle Name:')
    last_name = StringField(label='Last Name:',validators=[DataRequired()])
    city = SelectField(label='City:',choices=cities)
    home_address = StringField(label='Home Address:',validators=[DataRequired()])
    contact_number = StringField(label='Contact Number:',validators=[Length(max=13),DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    birthdate = DateField(label='Birth Date:',validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:',validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    def validate_password(self, pass_to_check):
        password = user_information.query.filter_by(pwd=pass_to_check.data).first()
        
        if password == None:
            raise ValidationError('Incorrect Password')

    emailadd = StringField(label='Email Address:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class RescheduleForm(FlaskForm):
    def validate_password(self, pass_to_check):
        password = user_information.query.filter_by(pwd=pass_to_check.data).first()
        
        if password == None:
            raise ValidationError('Incorrect Password')

    emailadd2 = StringField(label='Email Address:', validators=[DataRequired()])
    password2 = PasswordField(label='Password:', validators=[DataRequired()])
    submit2 = SubmitField(label='Sign in')

class AdminLoginForm(FlaskForm):
    def validate_hosid(self, pass_to_check):
        hosid = hospital.query.filter_by(hosp_id=pass_to_check.data).first()
        if hosid is None:
            raise ValidationError('Incorrect Password')
    hosname = StringField(label='Hospital Name:', validators=[DataRequired()])
    hosid = PasswordField(label='Hospital ID:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class UpdateItemForm(FlaskForm):
    submit = SubmitField(label='Update')
    delete = SubmitField(label='Delete')
    

class NonValidatingSelectField(SelectField):
    def pre_validate(self, UpdateVaccineForm):
        pass 

class UpdateVaccineForm(FlaskForm):
    vaccinedate = DateField(label='Vaccine Date:')
    time1 = TimeField()
    time2 = TimeField()
    update = SubmitField(label='Update')
    add = SubmitField(label='Add')
    deletesched = SubmitField(label='Delete')
    addtime = SubmitField(label='Update Schedule')

class AddVaccineForm(FlaskForm):
    vaccinename=StringField(label='Vaccine Name:', validators=[DataRequired()])
    expiration=DateField(label='Vaccine Date:',validators=[DataRequired()])
    supplier=StringField(label='Vaccine Name:', validators=[DataRequired()])
    manufacturer=StringField(label='Vaccine Name:', validators=[DataRequired()])
    information=StringField(label='Vaccine Name:')
   
    vaccinetype= SelectField = SelectField(label="Expected Date of Vaccination:", choices=["booster","not booster"])
    add = SubmitField(label='Add')

class AddAppointmentForm(FlaskForm):
    all_hospitals = [hosp.hosp_name for hosp in hospital.query.filter_by().all()]
    hospitalname = SelectField(label="Hospital Name:", validators=[DataRequired()], choices=all_hospitals)

    hospitaladdress = StringField(label="Hospital Address:", validators=[DataRequired()])

    all_vaccines = [vac.vaccine_name for vac in vaccine.query.filter_by().all()]
    availablevaccines = SelectField(label='Available Vaccines: ', choices=all_vaccines)

    all_sched = [sched.availability_date for sched in availability_details.query.filter_by().all()]
    vaccineschedule: SelectField = SelectField(label="Expected Date of Vaccination:", choices=all_sched)

    vaccinetime = StringField(label="Time:", validators=[DataRequired()])

    
    vaccinetype= StringField(label="Dose:", validators=[DataRequired()])

    schedule = SubmitField(label='Make Appointment')

