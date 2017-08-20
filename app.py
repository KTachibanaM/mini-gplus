from flask import Flask, request, render_template, redirect, url_for
from mongoengine import NotUniqueError
from flask_mongoengine import MongoEngine
from forms import SignupForm
from models import User

app = Flask(__name__, template_folder='templates')
db = MongoEngine(app)


@app.route("/")
def index():
    return render_template('index.jinja2')


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
