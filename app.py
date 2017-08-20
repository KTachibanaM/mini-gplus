from flask import Flask, request, render_template, redirect, url_for, abort
from mongoengine import NotUniqueError
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm
from models import User, Circle
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
    if not current_user.is_authenticated:
        signin_form = SigninForm(request.form)
        if request.method == 'POST' and signin_form.validate():
            users = User.objects(user_id=signin_form.id.data, password=signin_form.password.data)
            if not users:
                signin_form.id.errors.append('Wrong id or password')
                signin_form.password.errors.append('Wrong id or password')
            elif len(users) > 1:
                return abort(500)
            else:
                login_user(users[0], remember=True)
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(url_for('index'))
        return render_template('signin.jinja2', form=signin_form)
    else:
        return render_template('index.jinja2')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm(request.form)
    if request.method == 'POST' and signup_form.validate():
        new_user = User()
        new_user.user_id = signup_form.id.data
        new_user.password = signup_form.password.data
        try:
            new_user.save()
        except NotUniqueError:
            signup_form.id.errors.append('id {} is already taken'.format(signup_form.id.data))
        else:
            return redirect(url_for('index'))
    return render_template('signup.jinja2', form=signup_form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/users')
@login_required
def users():
    return render_template('users.jinja2', users=User.objects())


@app.route('/circles', methods=['GET', 'POST'])
@login_required
def circles():
    create_new_circle_form = CreateNewCircleForm(request.form)
    if request.method == 'POST' and create_new_circle_form.validate():
        new_circle_name = create_new_circle_form.name.data
        if Circle.objects(owner=current_user.id, name=new_circle_name):
            create_new_circle_form.name.errors.append('Circle {} already exists'.format(new_circle_name))
        else:
            new_circle = Circle()
            new_circle.owner = current_user.id
            new_circle.name = new_circle_name
            new_circle.save()
    return render_template('circles.jinja2', form=create_new_circle_form, circles=Circle.objects(owner=current_user.id))

if __name__ == '__main__':
    app.run()
