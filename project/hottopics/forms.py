from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from hottopics.models import Users

class Registration(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16), Regexp('^\w+$')])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=6)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is already in use.")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already in use.")


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg", "jpeg", "png"])])
    submit = SubmitField('Update account')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is already in use.")

    def validate_email(self, email):
        if current_user.email != email.data:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("That email is already in use.")

class PasswordChange(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class CreatePost(FlaskForm):
    content = TextAreaField('Post Content', validators=[DataRequired(), Length(max=150)])
    choice_1 = StringField('Choice #1', validators=[DataRequired(), Length(max=40)])
    choice_2 = StringField('Choice #2', validators=[DataRequired(), Length(max=40)])
    choice_3 = StringField('Choice #3', validators=[Length(max=40)])
    choice_4 = StringField('Choice #4', validators=[Length(max=40)])
    submit = SubmitField('Create Post') 

 