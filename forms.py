from wtforms import Form, StringField, BooleanField, PasswordField, TextAreaField, validators, SelectMultipleField
from utils import DataRequiredIf
from bson.objectid import ObjectId


class SignupForm(Form):
    id = StringField('ID', [
        validators.DataRequired(),
        validators.Length(min=2, max=256)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')


class SigninForm(Form):
    id = StringField('ID', [
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


class CreateNewCircleForm(Form):
    name = StringField('Name', [
        validators.DataRequired()
    ])


class CreateNewPostForm(Form):
    content = TextAreaField('Content', [
        validators.DataRequired()
    ])
    is_public = BooleanField('Is public')
    circles = SelectMultipleField('Circles', [
        DataRequiredIf(is_public=False)
    ], ObjectId)
