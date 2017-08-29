from flask import flash, redirect
from wtforms.validators import Optional, DataRequired
from urlparse import urlparse, urljoin


def flash_error(error_msg):
    flash(error_msg, 'error')


def _is_safe_url(request, target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _get_redirect_target(request):
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if _is_safe_url(request, target):
            return target
    return None


def redirect_back(request, default_target='/'):
    redirect_target = _get_redirect_target(request)
    if not redirect_target:
        return redirect(default_target)
    else:
        return redirect(redirect_target)


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
