# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

from flask_login import login_required, logout_user

# Import module forms
from app.user.forms import LoginForm, RegistrationForm
from app.user.models import User, UserRepository


# Define the blueprint: 'auth', set its url prefix: app.url/auth
user = Blueprint('user', __name__, url_prefix='/user')

# Set the route and accepted methods


@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = UserRepository.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            session['user_id'] = user.session_token
            flash('Welcome %s' % user.username)
            return redirect(url_for('home_page'))
        flash('Wrong email or password', 'danger')
    return render_template("user/login.html", form=form)

# Set the route and accepted methods


@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = UserRepository.find_by_email(form.email.data)
        if user:
            flash('Email is already taken.', 'danger')
            return render_template("user/register.html", form=form)
        user = User(form.username.data, form.email.data)
        user.set_password(form.password.data)
        user = UserRepository.create(user)
        if user:
            session['user_id'] = user.session_token
            flash('Welcome %s' % user.username)
            return redirect(url_for('home_page'))
        else:
            flash('Something went wrong.', 'danger')
    return render_template("user/register.html", form=form)


@user.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))
