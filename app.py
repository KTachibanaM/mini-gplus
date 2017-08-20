from flask import Flask, request, render_template, redirect, url_for, abort
from mongoengine import NotUniqueError
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, login_user
from forms import SignupForm, SigninForm
from models import User
from utils import is_safe_url
from os import urandom

app = Flask(__name__, template_folder='templates')
app.secret_key = urandom(24)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
db = MongoEngine(app)


@login_manager.user_loader
def load_user(id):
    users = User.objects(id=id)
    if len(users) == 1:
        return users[0]
    else:
        return None


@app.route("/", methods=['GET', 'POST'])
def index():
    form = SigninForm(request.form)
    if request.method == 'POST' and form.validate():
        users = User.objects(user_id=form.id.data, password=form.password.data)
        if not users:
            form.id.errors.append('Wrong id or password')
            form.password.errors.append('Wrong id or password')
        elif len(users) > 1:
            return abort(500)
        else:
            login_user(users[0], remember=True)
            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)
            return 'logged in!'
    return render_template('signin.jinja2', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        new_user = User()
        new_user.user_id = form.id.data
        new_user.password = form.password.data
        try:
            new_user.save()
        except NotUniqueError:
            form.id.errors.append('id {} is already taken'.format(form.id.data))
            return render_template('signup.jinja2', form=form)
        return redirect(url_for('index'))
    else:
        return render_template('signup.jinja2', form=form)

if __name__ == '__main__':
    app.run()
