from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import InputRequired, Length, EqualTo, Email, DataRequired, ValidationError


class RegistrationForm(FlaskForm):
    def __init__(self, cursor, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.cursor = cursor

    def validate_username(self, username_to_check):
        self.cursor.execute("SELECT * FROM User WHERE username = %s", (username_to_check.data,))
        user = self.cursor.fetchone()
        if user:
            raise ValidationError('Username already exists! Please try a different username.')

    def validate_email_address(self, email_address_to_check):
        self.cursor.execute("SELECT * FROM User WHERE email_address = %s", (email_address_to_check.data,))
        email_address = self.cursor.fetchone()
        if email_address:
            raise ValidationError('Email address already exists! Please try a different email.')


    username = StringField(label='Username', validators=[InputRequired(message="Username required"), Length(min=4, max=32, message="Username must be between 4 and 32 characters"), DataRequired()])
    firstname = StringField(label='First Name', validators=[InputRequired(message="First name required"), Length(min=1, message="First name must be at least 1 character"), DataRequired()])
    lastname = StringField(label='Last Name', validators=[InputRequired(message="Last name required"), Length(min=1, message="Last name must be at least 1 character"), DataRequired()])
    email_address = StringField(label='Email', validators=[Email(message="Invalid Email address"), DataRequired()])
    password1 = PasswordField(label='Password', validators=[InputRequired(message="Password required"), Length(min=4, max=32, message="Password must be between 4 and 32 characters"), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[InputRequired(message="Password required"), EqualTo('password1', message="Passwords must match"), DataRequired()])
    user_type = RadioField(label='Select one of the following:', choices=[('insurance_provider', 'Insurance Provider'), ('hospital', 'Hospital')], validators=[InputRequired(message="Select one option"), DataRequired()])
    submit = SubmitField(label='Submit')
    
#Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message="Username required"), DataRequired()])
    password = PasswordField('Password', validators=[InputRequired(message="Password required"), DataRequired()])
    submit = SubmitField('Log In')

#Form to get the name of either the hospital or the insurance provider, this is currently a seperate page right after login
class GetNameForm(FlaskForm):
    hospital_name = StringField(label='Hospital Name')
    insurance_name = StringField(label='Insurance Name')
    submit = SubmitField(label='Submit')

class addHospitalForm(FlaskForm):
    name = StringField(label='Hospital Name')
    address = StringField(label='Address')
    phone_number = StringField(label='Phone Number')
    submit = SubmitField(label='Add Hospital')

class addInsuranceForm(FlaskForm):
    name = StringField(label='Insurance Company Name')
    phone_number = StringField(label='Phone Number')
    submit = SubmitField(label='Add Insurance')