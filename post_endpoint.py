from urlparse import urlparse, urljoin
from flask import request
from flask_login import login_required


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def post_endpoint(app, route):
    @app.route(route, methods=['POST'])
    @login_required
    def decorator(route_func):
        def wrapper(*args, **kwargs):
            route_func(*args, **kwargs)
        return wrapper
    return decorator
