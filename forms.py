from wtforms import Form, StringField, PasswordField, validators


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
