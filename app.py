from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm, CreateNewPostForm
from models import User as DbUser
from models import Circle, Post, Comment
from utils import flash_error, redirect_back
from os import urandom
import os
import sys
from pymongo.uri_parser import parse_uri
from custom_exceptions import UnauthorizedAccess
from flask_restful import Api
from resources.user import UserList, Me
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token

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
    return DbUser.objects.get(id=loaded_id)


@app.context_processor
def inject_user():
    return dict(user=current_user)


user = current_user  # type: Me


@app.route('/')
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
        found_user = DbUser.check(signin_form.id.data, signin_form.password.data)
        if found_user:
            login_user(found_user, remember=True)
        else:
            flash_error('Wrong id or password')
    signin_form.flash_all_errors()
    return redirect(url_for('index'))


@app.route('/signup')
def signup():
    return render_template('signup.jinja2', form=SignupForm())


@app.route('/add-user', methods=['POST'])
def add_user():
    signup_form = SignupForm(request.form)
    if signup_form.validate():
        if DbUser.create(signup_form.id.data, signup_form.password.data):
            return redirect(url_for('index'))
        flash_error('id {} is already taken'.format(signup_form.id.data))
    signup_form.flash_all_errors()
    return redirect(url_for('signup'))


@app.errorhandler(UnauthorizedAccess)
def unauthorized(error):
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
    return redirect_back(request, url_for('index'))


@app.route('/rm-post', methods=['POST'])
@login_required
def rm_post():
    post = Post.objects.get(id=request.form.get('id'))
    user.delete_post(post)
    return redirect_back(request, url_for('index'))


@app.route('/reply/<post_id>')
@app.route('/reply/<post_id>/<comment_id>')
@login_required
# TODO: authorized?
def reply(post_id, comment_id=None):
    return render_template('reply.jinja2', post_id=post_id, comment_id=comment_id, next=request.args.get('next', url_for('index')))


@app.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    user.create_comment(request.form.get('content'), post)
    return redirect_back(request, url_for('index'))


@app.route('/add-nested-comment', methods=['POST'])
@login_required
def add_nested_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    user.create_nested_comment(request.form.get('content'), comment, post)
    return redirect_back(request, url_for('index'))


@app.route('/rm-comment', methods=['POST'])
@login_required
def rm_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    user.delete_comment(comment, post)
    return redirect_back(request, url_for('index'))


@app.route('/rm-nested-comment', methods=['POST'])
@login_required
def rm_nested_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    parent_comment = Comment.objects.get(id=request.form.get('parent_comment_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    user.delete_nested_comment(comment, parent_comment, post)
    return redirect_back(request, url_for('index'))


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
        users=DbUser.objects(id__ne=user.id),
        circles=Circle.objects(owner=user.id))


@app.route('/circles')
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
        if not user.create_circle(new_circle_name):
            flash_error('{} already exists'.format(new_circle_name))
    create_new_circle_form.flash_all_errors()
    return redirect_back(request, url_for('index'))


@app.route('/toggle-member', methods=['POST'])
@login_required
def toggle_member():
    circle = Circle.objects.get(id=request.form.get('circle_id'))  # type: Circle
    toggled_user = DbUser.objects.get(id=request.form.get('user_id'))
    user.toggle_member(circle, toggled_user)
    return redirect_back(request, url_for('index'))


@app.route('/rm-circle', methods=['POST'])
@login_required
def rm_circle():
    circle = Circle.objects.get(id=request.form.get('id'))
    user.delete_circle(circle)
    return redirect_back(request, url_for('index'))


@app.route('/profile/<user_id>')
@login_required
def public_profile(user_id):
    profile_user = DbUser.objects.get(user_id=user_id)
    return render_template('profile.jinja2', profile_user=profile_user, posts=user.sees_posts(profile_user))


##################
# Authentication #
##################
app.config['JWT_SECRET_KEY'] = '123456'  # TODO: read from env
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
JWTManager(app)


@app.route('/api/auth', methods=['POST'])
def auth():
    if not request.is_json:
        return jsonify({"message": "missing JSON in request"}), 400
    id = request.json.get('id', None)
    password = request.json.get('password', None)
    if not id:
        return jsonify({"message": {"id": "id is required"}}), 400
    if not password:
        return jsonify({"message": {"password": "password is required"}}), 400
    user_checked = DbUser.check(id, password)
    if not user_checked:
        return jsonify({"message": "invalid id or password"}), 401
    access_token = create_access_token(identity=id)
    return jsonify(access_token=access_token), 200


########
# APIs #
########
app.config['BUNDLE_ERRORS'] = True
CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app)
api.add_resource(UserList, '/api/users')
api.add_resource(Me, '/api/me')

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'c9':
        app.run(host='0.0.0.0', port=8080)
    else:
        app.run(host='localhost', port=5000)
