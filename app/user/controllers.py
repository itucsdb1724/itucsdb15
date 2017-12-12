import datetime
import copy

from functools import reduce

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, abort

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

from flask_login import login_required, logout_user, current_user

# Import module forms
from app.user.forms import LoginForm, RegistrationForm, EditForm

#Import models
from app.user.models import User, UserRepository
from app.section.models import SectionRepository
from app.message.models import MessageRepository
from app.file.models import FileRepository


user = Blueprint('user', __name__, url_prefix='/user')



@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = UserRepository.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            session['user_id'] = user.session_token
            flash('Welcome %s' % user.username, 'success')
            return redirect(url_for('home_page'))
        flash('Wrong email or password', 'danger')
    return render_template("user/form.html", form=form, title="Login")



@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = UserRepository.find_by_email(form.email.data)
        if user:
            flash('Email is already taken.', 'danger')
            return render_template("user/form.html", form=form, title="Register")
        user = User(form.username.data, form.email.data)
        user.set_password(form.password.data)
        user = UserRepository.create(user)
        if user:
            session['user_id'] = user.session_token
            flash('Welcome %s' % user.username, 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Something went wrong.', 'danger')
    return render_template("user/form.html", form=form, title="Register")


@user.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@user.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(request.form)
    if form.validate_on_submit():
        user = UserRepository.find_by_email(form.email.data)
        if (form.email.data != current_user.email) and UserRepository.find_by_email(form.email.data):
            flash('Email is already taken.', 'danger')
            return render_template("user/form.html", form=form)
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template("user/form.html", form=form, title="Edit Profile")
        new_user = copy.copy(current_user)
        new_user.email = form.email.data
        new_user.username = form.username.data
        new_user.updated_at = datetime.datetime.now()
        if form.password.data:
            new_user.set_password(form.password.data)
        if UserRepository.update(current_user, new_user):
            flash('Your profile is updated.')
            return render_template("user/form.html", form=form, title="Edit Profile")
        else:
            flash('Something went wrong.', 'danger')
    else:
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template("user/form.html", form=form, title="Edit Profile")


@user.route('/<int:id>', methods=['GET'])
def show(id):
    user = UserRepository.find_by_id(id)
    if not user:
        abort(404)
    messages = MessageRepository.find_messages_of_user(id)
    files = FileRepository.find_files_of_user(id)
    def map_model_to_dict(x, model):
        x.update({str(model.id): model})
        return x
    sections = reduce(map_model_to_dict, SectionRepository.all(), {})
    return render_template("user/show.html", user=user, messages=messages, files=files, sections=sections)
