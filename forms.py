from utils import flash_error
from wtforms import Form, StringField, BooleanField, PasswordField, TextAreaField, validators, SelectMultipleField
from utils import DataRequiredIf
from bson.objectid import ObjectId
from models import Circle


class AllErrorsStrMixin(object):
    @property
    def all_errors_str(self):
        for field, errors in self.errors.items():
            for error in errors:
                yield "{}: {}".format(field, error)


class FlashAllErrorsMixin(AllErrorsStrMixin):
    def flash_all_errors(self):
        for error in self.all_errors_str:
            flash_error(error)


class SignupForm(Form, FlashAllErrorsMixin):
    id = StringField('ID', [
        validators.DataRequired(),
        validators.Length(min=2, max=256)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')


class SigninForm(Form, FlashAllErrorsMixin):
    id = StringField('ID', [
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


class CreateNewCircleForm(Form, FlashAllErrorsMixin):
    name = StringField('Name', [
        validators.DataRequired()
    ])


class CreateNewPostForm(Form, FlashAllErrorsMixin):
    content = TextAreaField('Content', [
        validators.DataRequired()
    ])
    is_public = BooleanField('Is public')
    circles = SelectMultipleField('Circles', [
        DataRequiredIf(is_public=False)
    ], ObjectId)

    def __init__(self, circles, *args, **kwargs):
        """
        :param (list[Circle]) circles: circles
        :param args:
        :param kwargs:
        """
        super(CreateNewPostForm, self).__init__(*args, **kwargs)
        self.circles.choices = map(
            lambda circle: (circle.id, circle.name),
            circles
        )
