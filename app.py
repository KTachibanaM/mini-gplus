from flask import Flask, request, render_template, redirect, url_for, abort
from mongoengine import NotUniqueError
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm, CreateNewPostForm
from models import User, Circle, Post, Comment
from utils import flash_error
from os import urandom
from bson.objectid import ObjectId
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


@app.route("/", methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return render_template('signin.jinja2', form=SigninForm())
    else:
        create_new_post_form = CreateNewPostForm()
        create_new_post_form.circles.choices = map(
            lambda circle: (circle.id, circle.name),
            Circle.objects(owner=current_user.id)
        )
        posts = filter(lambda post: post.shared_with(current_user), Post.objects())
        posts = list(reversed(sorted(posts, key=lambda post: post.created_at)))
        return render_template('index.jinja2', form=create_new_post_form, posts=posts)


@app.route('/signin', methods=['POST'])
def signin():
    signin_form = SigninForm(request.form)
    if signin_form.validate():
        found_user = User.check(signin_form.id.data, signin_form.password.data)
        if found_user:
            login_user(found_user, remember=True)
        else:
            flash_error('Wrong id or password')
    else:
        for error in signin_form.all_errors_str:
            flash_error(error)
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
    for error in signup_form.all_errors_str:
        flash_error(error)
    return redirect(url_for('signup'))


@app.route('/add-post', methods=['POST'])
@login_required
def add_post():
    create_new_post_form = CreateNewPostForm(request.form)
    create_new_post_form.circles.choices = map(
        lambda circle: (circle.id, circle.name),
        Circle.objects(owner=current_user.id)
    )
    if create_new_post_form.validate():
        new_post = Post()
        new_post.author = current_user.id
        new_post.content = create_new_post_form.content.data
        new_post.is_public = create_new_post_form.is_public.data
        new_post.circles = create_new_post_form.circles.data
        new_post.save()
    else:
        for error in create_new_post_form.all_errors_str:
            flash_error(error)
    return redirect(url_for('index'))


@app.route('/rm-post', methods=['POST'])
@login_required
def rm_post():
    post = Post.objects.get(id=request.form.get('id'))
    if post.author.id == current_user.id:
        post.delete()
    return redirect(url_for('index'))


@app.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    if post.shared_with(current_user):
        new_comment = Comment()
        new_comment.author = current_user.id
        new_comment.content = request.form.get('content')
        new_comment.save()
        post.comments.append(new_comment)
        post.save()
    return redirect(url_for('index'))


@app.route('/rm-comment', methods=['POST'])
@login_required
def rm_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    if comment.owned_by(current_user, post):
        post.comments.remove(comment)
        comment.delete()
    return redirect(url_for('index'))


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
        users=User.objects(id__ne=current_user.id),
        circles=Circle.objects(owner=current_user.id)
    )


@app.route('/circles', methods=['GET'])
@login_required
def circles():
    form = CreateNewCircleForm()
    return render_template('circles.jinja2', form=form, circles=Circle.objects(owner=current_user.id))


@app.route('/add-circle', methods=['POST'])
@login_required
def add_circle():
    form = CreateNewCircleForm(request.form)
    if form.validate():
        new_circle_name = form.name.data
        if not Circle.create(current_user, new_circle_name):
            flash_error('{} already exists'.format(new_circle_name))
    else:
        for error in form.all_errors_str:
            flash_error(error)
    return redirect(url_for('circles'))


@app.route('/toggle-member', methods=['POST'])
@login_required
def toggle_member():
    circle = Circle.objects.get(id=request.form.get('circle_id'))  # type: Circle
    if circle.owner.id == current_user.id:
        toggled_user = User.objects.get(id=request.form.get('user_id'))
        if circle.check_member(toggled_user):
            circle.members.remove(toggled_user)
        else:
            circle.members.append(toggled_user)
        circle.save()
    return redirect(url_for('users'))


@app.route('/rm-circle', methods=['POST'])
@login_required
def rm_circle():
    circle = Circle.objects.get(id=request.form.get('id'))
    if circle.owner.id == current_user.id:
        circle.delete()
    return redirect(url_for('circles'))


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    posts = list(reversed(sorted(Post.objects(author=current_user.id), key=lambda post: post.created_at)))
    return render_template('profile.jinja2', user_id=current_user.user_id, posts=posts)


@app.route('/profile/<public_id>', methods=['GET'])
@login_required
def public_profile(public_id):
    posts = filter(lambda post: post.shared_with(current_user), Post.objects(author=ObjectId(public_id)))
    posts = list(reversed(sorted(posts, key=lambda post: post.created_at)))
    return render_template('profile.jinja2', user_id=User.objects.get(id=public_id).user_id, posts=posts)

if __name__ == '__main__':
    app.run()
