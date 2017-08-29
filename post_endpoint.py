from urlparse import urlparse, urljoin
from flask import redirect
from flask_login import login_required


def is_safe_url(request, target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target(request):
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
    return None

def redirect_back(request, default_target='/'):
    redirect_target = get_redirect_target(request)
    if not redirect_target:
        return redirect(default_target)
    else:
        return redirect(redirect_target)