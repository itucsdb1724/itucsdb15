import os
import uuid

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.utils import secure_filename

from flask import current_app as app

from app.course.models import CourseRepository
from app.file.models import File, FileRepository
from app.message.models import Message, MessageRepository
from app.section.models import SectionRepository

from app.file.forms import NewFileForCourseForm
from app.message.forms import NewThreadForCourseForm
from app.message.forms import NewMessageForm


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



@course.route('/<int:id>/files', methods=['GET', 'POST'])
def files(id):
    course = CourseRepository.find_by_id(id)
    if not course:
        abort(404)
    files = FileRepository.find_files_of_course(course.id)
    form = NewFileForCourseForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(f.filename)[1])
        f.save(os.path.join(app.config['UPLOAD_DIR'], 'files', filename))
        file = File()
        file.course_id = course.id
        file.user_id = current_user.id
        file.title = form.title.data
        file.filename = filename
        file.original_filename = f.filename
        file.content_type = f.content_type
        file = FileRepository.create(file)
        return redirect(url_for('course.files', id=id))
    return render_template("course/files.html", course=course, files=files, form=form, current_user=current_user)


@course.route('/<int:id>/messages', methods=['GET', 'POST'])
def threads(id):
    course = CourseRepository.find_by_id(id)
    if not course:
        abort(404)
    threads = MessageRepository.find_threads_of_course(course.id)
    form = NewThreadForCourseForm()
    if form.validate_on_submit():
        message = Message()
        message.course_id = course.id
        message.user_id = current_user.id
        message.title = form.title.data
        message.message = form.message.data
        message = MessageRepository.create(message)
        return redirect(url_for('course.threads', id=id))
    return render_template("course/threads.html", course=course, threads=threads, form=form, current_user=current_user)

@course.route('/<int:course_id>/messages/<int:id>', methods=['GET', 'POST'])
def messages(course_id, id):
    course = CourseRepository.find_by_id(course_id)
    if not course:
        abort(404)
    thread = MessageRepository.find_by_id(id)
    if not thread:
        abort(404)
    if thread.course_id != course.id:
        abort(404)
    messages = MessageRepository.find_messages_of_thread(id)
    form = NewMessageForm()
    if form.validate_on_submit():
        message = Message()
        message.course_id = course.id
        message.user_id = current_user.id
        message.title = thread.title
        message.thread_id = thread.id
        message.message = form.message.data
        message = MessageRepository.create(message)
        return redirect(url_for('course.messages', course_id=course_id, id=id))
    return render_template("course/messages.html", course=course, messages=messages, form=form, current_user=current_user, thread=thread)



@course.route('/find', methods=['GET'])
def find():
	department_code = request.args.get('department_code')
	course_code = request.args.get('course_code')
	course = CourseRepository.find_by_department_and_course_code(department_code, course_code)
	if course is not None:
		return redirect(url_for('course.index', id=course.id))
	flash('No course found ' + department_code + course_code, 'danger')
	return redirect(url_for('home_page'))
