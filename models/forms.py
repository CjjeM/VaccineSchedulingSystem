from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,DateField,TimeField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models.models import user_information, hospital

cities = ['Alaminos', 'Bay', 'Biñan', 'Cabuyao','Calamba','Calauan','Cavinti','Famy','Kalayaan','Liliw',
    'Los Baños','Luisiana','Lumban','Mabitac','Magdalena','Majayjay','Nagcarlan','Paete','Pagsanjan','Pakil',
    'Pangil','Pila','Rizal','San Pablo','San Pedro','Santa Cruz','Santa Maria','Sta. Rosa','Siniloan','Victoria']
vactime=['1','2','3','4','5','6','7','8','9','10','11','12']
timeofday=['AM','PM']

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
    contact_number = StringField(label='Contact Number:',validators=[Length(max=6),DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    birthdate = DateField(label='Birth Date:',validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:',validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    emailadd = StringField(label='Email Address:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class AdminLoginForm(FlaskForm):
    def validate_hosid(self, pass_to_check):
        hosid = hospital.query.filter_by(id=pass_to_check.data).first()
        if hosid is None:
            raise ValidationError('Incorrect Password')
    hosname = StringField(label='Hospital Name:', validators=[DataRequired()])
    hosid = PasswordField(label='Hospital ID:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class UpdateItemForm(FlaskForm):
    submit = SubmitField(label='Update')

class DeleteItemForm(FlaskForm):
    delete = SubmitField(label='Delete')

class UpdateSchedForm(FlaskForm):
    update = SubmitField(label='Update')

class AddSchedForm(FlaskForm):
    add = SubmitField(label='Add')

class DeleteSchedForm(FlaskForm):
    deletesched = SubmitField(label='Delete')

class NonValidatingSelectField(SelectField):
    def pre_validate(self, UpdateVaccineForm):
        pass 

class UpdateVaccineForm(FlaskForm):
    vaccinedate = DateField(label='Vaccine Date:',validators=[DataRequired()])
    time1 = TimeField()
    time2 = TimeField()
    addtime = SubmitField(label='Update Schedule')

class AddVaccineForm(FlaskForm):
    vaccinename=StringField(label='Vaccine Name:', validators=[DataRequired()])
    add = SubmitField(label='Add')

