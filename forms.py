from wtforms import Form, StringField, BooleanField, PasswordField, validators
from utils import DataRequiredIf, MultiCheckboxField
from bson.objectid import ObjectId


class SignupForm(Form):
    id = StringField('id', [
        validators.DataRequired(),
        validators.Length(min=2, max=256)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Repeat Password')


class SigninForm(Form):
    id = StringField('id', [
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


class CreateNewCircleForm(Form):
    name = StringField('New circle name', [
        validators.DataRequired()
    ])


class CreateNewPostForm(Form):
    content = StringField('New post', [
        validators.DataRequired()
    ])
    is_public = BooleanField('Public')
    circles = MultiCheckboxField('Circles', [
        DataRequiredIf(is_public=False)
    ], ObjectId)
