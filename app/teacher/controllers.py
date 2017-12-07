# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user


teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher.route('/<int:id>', methods=['GET'])
def index(id):
    return render_template("teacher/index.html")