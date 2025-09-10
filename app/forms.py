
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")

class ApplicationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    national_id = StringField("National ID", validators=[DataRequired(), Regexp(r"^\d{11}$", message="Must be 11 digits")])
    birth_date = StringField("Birth Date (yyyy-mm-dd)", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired(), Length(min=5, max=255)])
    passport_type = SelectField("Passport Type", choices=[
        ("Ordinary","Ordinary Passport"),("Service","Service Passport"),("Special","Special Passport")
    ], validators=[DataRequired()])
    submit = SubmitField("Submit Application")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send reset link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Set new password")

from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")
