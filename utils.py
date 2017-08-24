from flask import flash
from wtforms.validators import Optional, DataRequired


def flash_error(error_msg):
    flash(error_msg, 'error')


class DataRequiredIf(object):
    """Validates field conditionally.

    Usage:
        login_method = StringField('', [AnyOf(['email', 'facebook'])])
        email = StringField('', [RequiredIf(login_method='email')])
        password = StringField('', [RequiredIf(login_method='email')])
        facebook_token = StringField('', [RequiredIf(login_method='facebook')])
    """
    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.iteritems():
            if name not in form._fields:
                Optional(form, field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data and not field.data:
                    DataRequired()(form, field)
        Optional()(form, field)
