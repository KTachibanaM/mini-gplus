from flask import Flask, request, render_template, redirect, url_for, abort
from mongoengine import NotUniqueError, Q
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import SignupForm, SigninForm, CreateNewCircleForm, CreateNewPostForm
from models import User, Circle, Post
from utils import is_safe_url
from os import urandom

app = Flask(__name__, template_folder='templates')
app.secret_key = urandom(24)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)


@login_manager.user_loader
def load_user(loaded_id):
    return User.objects.get(id=loaded_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        signin_form = SigninForm(request.form)
        if request.method == 'POST' and signin_form.validate():
            found_users = User.objects(user_id=signin_form.id.data, password=signin_form.password.data)
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

        def is_accessible(post):
            if post.author.id == current_user.id:
                return True
            elif post.is_public:
                return True
            else:
                for circle in post.circles:
                    if circle.is_member(current_user):
                        return True
            return False

        return render_template('index.jinja2', form=create_new_post_form, posts=filter(is_accessible, Post.objects()))


@app.route('/rmpost', methods=['POST'])
@login_required
def rm_post():
    post = Post.objects.get(id=request.form.get('id'))
    if post.author.id == current_user.id:
        post.delete()
    return redirect(url_for('index'))


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
def toggle_member():
    circle = Circle.objects.get(id=request.form.get('circle_id'))  # type: Circle
    user = User.objects.get(id=request.form.get('user_id'))
    if circle.is_member(user):
        circle.members.remove(user)
    else:
        circle.members.append(user)
    circle.save()
    return redirect(url_for('users'))


@app.route('/rmcircle', methods=['POST'])
@login_required
def rm_circle():
    circle = Circle.objects.get(id=request.form.get('id'))
    if circle.owner.id == current_user.id:
        circle.delete()
    return redirect(url_for('circles'))


if __name__ == '__main__':
    app.run()
