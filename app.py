from flask import Flask, request, render_template, redirect, url_for, abort
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm, CreateNewPostForm
from models import User, Circle, Post, Comment
from utils import flash_error
from os import urandom
import os
from pymongo.uri_parser import parse_uri

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = urandom(24)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/minigplus')
mongodb_db = parse_uri(mongodb_uri)['database']
app.config['MONGODB_SETTINGS'] = {
    'db': mongodb_db,
    'host': mongodb_uri
}
db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)


@login_manager.user_loader
def load_user(loaded_id):
    return User.objects.get(id=loaded_id)

user = current_user  # type: User


@app.route("/", methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return render_template('signin.jinja2', form=SigninForm())
    else:
        create_new_post_form = CreateNewPostForm(Circle.objects(owner=user.id))
        return render_template('index.jinja2', form=create_new_post_form, posts=user.sees_posts())


@app.route('/signin', methods=['POST'])
def signin():
    signin_form = SigninForm(request.form)
    if signin_form.validate():
        found_user = User.check(signin_form.id.data, signin_form.password.data)
        if found_user:
            login_user(found_user, remember=True)
        else:
            flash_error('Wrong id or password')
    signin_form.flash_all_errors()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.jinja2', form=SignupForm())


@app.route('/add-user', methods=['POST'])
def add_user():
    signup_form = SignupForm(request.form)
    if signup_form.validate():
        if User.create(signup_form.id.data, signup_form.password.data):
            return redirect(url_for('index'))
        flash_error('id {} is already taken'.format(signup_form.id.data))
    signup_form.flash_all_errors()
    return redirect(url_for('signup'))


@app.errorhandler(401)
def not_authorized(error):
    return 'Not authorized'


@app.route('/add-post', methods=['POST'])
@login_required
def add_post():
    create_new_post_form = CreateNewPostForm(Circle.objects(owner=user.id), request.form)
    if create_new_post_form.validate():
        user.create_post(
            create_new_post_form.content.data,
            create_new_post_form.is_public.data,
            create_new_post_form.circles.data)
    create_new_post_form.flash_all_errors()
    return redirect(url_for('index'))


@app.route('/rm-post', methods=['POST'])
@login_required
def rm_post():
    post = Post.objects.get(id=request.form.get('id'))
    if user.delete_post(post):
        return redirect(url_for('index'))
    abort(401)


@app.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    if user.create_comment(request.form.get('content'), post):
        return redirect(url_for('index'))
    abort(401)


@app.route('/rm-comment', methods=['POST'])
@login_required
def rm_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    if user.delete_comment(comment, post):
        return redirect(url_for('index'))
    abort(401)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/users')
@login_required
def users():
    return render_template(
        'users.jinja2',
        users=User.objects(id__ne=user.id),
        circles=Circle.objects(owner=user.id))


@app.route('/circles', methods=['GET'])
@login_required
def circles():
    form = CreateNewCircleForm()
    return render_template('circles.jinja2', form=form, circles=Circle.objects(owner=user.id))


@app.route('/add-circle', methods=['POST'])
@login_required
def add_circle():
    create_new_circle_form = CreateNewCircleForm(request.form)
    if create_new_circle_form.validate():
        new_circle_name = create_new_circle_form.name.data
        if not Circle.create(user, new_circle_name):
            flash_error('{} already exists'.format(new_circle_name))
    create_new_circle_form.flash_all_errors()
    return redirect(url_for('circles'))


@app.route('/toggle-member', methods=['POST'])
@login_required
def toggle_member():
    circle = Circle.objects.get(id=request.form.get('circle_id'))  # type: Circle
    if circle.owner.id == user.id:
        circle.toggle_member(User.objects.get(id=request.form.get('user_id')))
    return redirect(url_for('users'))


@app.route('/rm-circle', methods=['POST'])
@login_required
def rm_circle():
    circle = Circle.objects.get(id=request.form.get('id'))
    if circle.owner.id == user.id:
        circle.delete()
    return redirect(url_for('circles'))


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return redirect('/profile/{}'.format(user.user_id))


@app.route('/profile/<user_id>', methods=['GET'])
@login_required
def public_profile(user_id):
    profile_user = User.objects.get(user_id=user_id)
    return render_template('profile.jinja2', user_id=user_id, posts=user.sees_posts(profile_user))

if __name__ == '__main__':
    app.run()
