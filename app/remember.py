

_REMEMBER_COOKIE_NAME = 'remember-email'


def set_remember_me(req, resp):
    if req.form.get('rememberme', 'unchecked') == 'checked':
        resp.set_cookie(_REMEMBER_COOKIE_NAME, req.form['email'])


def get_remember_me(req):
    return req.cookies.get(_REMEMBER_COOKIE_NAME)
