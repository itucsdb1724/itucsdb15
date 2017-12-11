from flask_wtf import FlaskForm

from wtforms import BooleanField, StringField, PasswordField, SubmitField, validators


class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Email(),
                                          validators.Required(message='Forgot your email address?')])
    password = PasswordField('Password', [
        validators.Required(message='Must provide a password. ;-)')])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    current_password = PasswordField('Current Password', [validators.DataRequired()])
    password = PasswordField('New Password', [ validators.EqualTo('confirm', message='Passwords must match') ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Update')
