from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField,IntegerField
from wtforms.validators import InputRequired, Email

class RegisterForm(FlaskForm):
    form_username = StringField('Username', validators=[InputRequired()])
    form_password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    admin_code = StringField('Admin Code', render_kw={'type': 'password'})

class LoginForm(FlaskForm):
    form_username = StringField('Username', validators=[InputRequired()])
    form_password = PasswordField('Password', validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')