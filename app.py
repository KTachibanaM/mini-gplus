from flask import Flask, request, render_template, redirect, url_for, abort
from mongoengine import NotUniqueError
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm, CreateNewPostForm
from models import User, Circle, Post, Comment
from utils import is_safe_url
from os import urandom
from bson.objectid import ObjectId
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = urandom(24)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
db = MongoEngine(app, config={
    'host': os.environ.get('MONGODB_URI', 'localhost:27017')
})
app.session_interface = MongoEngineSessionInterface(db)


@login_manager.user_loader
def load_user(loaded_id):
    return User.objects.get(id=loaded_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        signin_form = SigninForm(request.form)
        if request.method == 'POST' and signin_form.validate():
            found_users = User.check(signin_form.id.data, signin_form.password.data)
            if not found_users:
                signin_form.id.errors.append('Wrong id or password')
                signin_form.password.errors.append('Wrong id or password')
            elif len(found_users) > 1:
                return abort(500)
            else:
                login_user(found_users[0], remember=True)
                next_arg = request.args.get('next')
                if not is_safe_url(next_arg):
                    return abort(400)
                return redirect(url_for('index'))
        return render_template('signin.jinja2', form=signin_form)
    else:
        current_circles = Circle.objects(owner=current_user.id)
        create_new_post_form = CreateNewPostForm(request.form)
        create_new_post_form.circles.choices = map(lambda circle: (circle.id, circle.name), current_circles)
        if request.method == 'POST' and create_new_post_form.validate():
            new_post = Post()
            new_post.author = current_user.id
            new_post.content = create_new_post_form.content.data
            new_post.is_public = create_new_post_form.is_public.data
            new_post.circles = create_new_post_form.circles.data
            new_post.save()

        posts = filter(lambda post: post.shared_with(current_user), Post.objects())
        posts = reversed(sorted(posts, key=lambda post: post.created_at))
        return render_template('index.jinja2', form=create_new_post_form, posts=posts)


@app.route('/rmpost', methods=['POST'])
@login_required
def rm_post():
    post = Post.objects.get(id=request.form.get('id'))
    if post.author.id == current_user.id:
        post.delete()
    return redirect(url_for('index'))


@app.route('/addcomment', methods=['POST'])
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


@app.route('/rmcomment', methods=['POST'])
@login_required
def rm_comment():
    post = Post.objects.get(id=request.form.get('post_id'))
    comment = Comment.objects.get(id=request.form.get('comment_id'))
    if comment.can_remove(current_user, post):
        post.comments.remove(comment)
        comment.delete()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm(request.form)
    if request.method == 'POST' and signup_form.validate():
        try:
            User.create(signup_form.id.data, signup_form.password.data)
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
    return render_template(
        'users.jinja2',
        users=User.objects(id__ne=current_user.id),
        circles=Circle.objects(owner=current_user.id)
    )


@app.route('/circles', methods=['GET', 'POST'])
@login_required
def circles():
    create_new_circle_form = CreateNewCircleForm(request.form)
    if request.method == 'POST' and create_new_circle_form.validate():
        new_circle_name = create_new_circle_form.name.data
        try:
            new_circle = Circle()
            new_circle.owner = current_user.id
            new_circle.name = new_circle_name
            new_circle.save()
        except NotUniqueError:
            create_new_circle_form.name.errors.append('Circle {} already exists'.format(new_circle_name))
    return render_template('circles.jinja2', form=create_new_circle_form, circles=Circle.objects(owner=current_user.id))


@app.route('/togglemember', methods=['POST'])
@login_required
def toggle_member():
    circle = Circle.objects.get(id=request.form.get('circle_id'))  # type: Circle
    if circle.owner.id == current_user.id:
        toggled_user = User.objects.get(id=request.form.get('user_id'))
        if circle.is_member(toggled_user):
            circle.members.remove(toggled_user)
        else:
            circle.members.append(toggled_user)
        circle.save()
    return redirect(url_for('users'))


@app.route('/rmcircle', methods=['POST'])
@login_required
def rm_circle():
    circle = Circle.objects.get(id=request.form.get('id'))
    if circle.owner.id == current_user.id:
        circle.delete()
    return redirect(url_for('circles'))


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    posts = reversed(sorted(Post.objects(author=current_user.id), key=lambda post: post.created_at))
    return render_template('profile.jinja2', user_id=current_user.user_id, posts=posts)


@app.route('/profile/<public_id>', methods=['GET'])
@login_required
def public_profile(public_id):
    posts = filter(lambda post: post.shared_with(current_user), Post.objects(author=ObjectId(public_id)))
    posts = reversed(sorted(posts, key=lambda post: post.created_at))
    return render_template('profile.jinja2', user_id=User.objects.get(id=public_id).user_id, posts=posts)

if __name__ == '__main__':
    app.run()
