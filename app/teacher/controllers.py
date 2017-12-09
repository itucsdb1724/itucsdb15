# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user

from app.teacher.models import TeacherRepository

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher.route('/<int:id>', methods=['GET'])
def index(id):
    return render_template("teacher/index.html")


@teacher.route('/search', methods=['GET'])
def search():
	query = request.args.get('query')
	teachers = TeacherRepository.search(query)
	return render_template("teacher/search.html", query=query, teachers=teachers)