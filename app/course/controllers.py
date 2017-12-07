# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user


course = Blueprint('course', __name__, url_prefix='/course')

@course.route('/<int:id>', methods=['GET'])
def index(id):
    return render_template("course/index.html")