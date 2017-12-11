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
@course.route('/<int:id>/messages', methods=['GET', 'POST'])
def threads(id):
    course = CourseRepository.find_by_id(id)
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
    thread = MessageRepository.find_by_id(id)
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
