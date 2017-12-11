# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for


from flask_login import login_required, logout_user

from app.course.models import CourseRepository
from app.section.models import SectionRepository


course = Blueprint('course', __name__, url_prefix='/course')

@course.route('/<int:id>', methods=['GET'])
def index(id):
	course = CourseRepository.find_by_id(id)
	if not course:
		abort(404)
	sections = SectionRepository.find_sections_of_course(id)
	return render_template("course/index.html", course=course, sections=sections)


# /search yapılacak
@course.route('/search', methods=['GET'])
def search():
	query = request.args.get('query')
	courses = CourseRepository.search(query)
	return render_template("course/search.html", query=query, courses=courses)


@course.route('/find', methods=['GET'])
def find():
	department_code = request.args.get('department_code')
	course_code = request.args.get('course_code')
	course = CourseRepository.find_by_department_and_course_code(department_code, course_code)
	if course is not None:
		return redirect(url_for('course.index', id=course.id))
	return render_template("course/no-course.html", department_code=department_code, course_code=course_code)