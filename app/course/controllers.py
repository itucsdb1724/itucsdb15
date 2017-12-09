# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user

from app.course.models import CourseRepository


course = Blueprint('course', __name__, url_prefix='/course')

@course.route('/<int:id>', methods=['GET'])
def index(id):
	course = CourseRepository.find_by_id(id)
	return render_template("course/index.html", course=course)


# /search yapılacak
@course.route('/search', methods=['GET'])
def search():
	query = request.args.get('query')
	courses = CourseRepository.search(query)
	return render_template("course/search.html", query=query, courses=courses)