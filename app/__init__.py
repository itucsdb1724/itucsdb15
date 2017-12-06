import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required


from app.user.controllers import user as user_module
from app.user.models import User, UserRepository
from app.teacher.models import Teacher, TeacherRepository
from app.course.models import Course, CourseRepository
from app.section.models import Section, SectionRepository

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(session_token):
    return UserRepository.find_by_session_token(session_token)


@app.route('/')
def home_page():
    now = datetime.datetime.now()
    teacher = TeacherRepository.find_by_id(1)
    course = CourseRepository.find_by_id(1)
    if teacher is None:
        teacher = TeacherRepository.create(Teacher("Sabih"))
    if course is None:
        course = CourseRepository.create(Course("BLG313","Giris"))
    section = Section()
    section.crn = 31228
    section.building = "EEB"
    section.day = "monday"
    section.time = "morning"
    section.room = "d212"
    section.capacity = 21
    section.enrolled = 12
    section.course_id =course.id
    section.teacher_id = teacher.id
    section = SectionRepository.create(section)

    return render_template('home.html', current_time=now.ctime(), user=user, teacher=teacher, course=course, section=section)


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER"""
        cursor.execute(query)

        query = """CREATE TABLE COUNTER (N INTEGER)"""
        cursor.execute(query)

        query = """INSERT INTO COUNTER (N) VALUES (0)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS users"""
        cursor.execute(query)

        query = """CREATE TABLE  users (
                  id serial PRIMARY KEY,
                  email varchar(255) NOT NULL,
                  username varchar(255) NOT NULL,
                  password varchar(255) NOT NULL,
                  session_token varchar(255) NOT NULL,
                  created_at timestamp,
                  updated_At timestamp
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS courses CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE courses (
                  id serial PRIMARY KEY,
                  course_code varchar(255) NOT NULL,
                  title varchar(255) NOT NULL,
                  created_at timestamp,
                  updated_At timestamp
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS teachers CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE teachers (
                  id serial PRIMARY KEY,
                  name varchar(255) NOT NULL,
                  created_at timestamp,
                  updated_At timestamp
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS sections"""
        cursor.execute(query)

        query = """CREATE TABLE sections (
                  id serial PRIMARY KEY,
                  course_id integer REFERENCES courses ON DELETE SET NULL ON UPDATE CASCADE,
                  teacher_id integer REFERENCES teachers  ON DELETE SET NULL ON UPDATE CASCADE,
                  crn varchar(255) NOT NULL,
                  building varchar(255) NOT NULL,
                  day varchar(255) NOT NULL,
                  time varchar(255) NOT NULL,
                  room varchar(255) NOT NULL,
                  capacity varchar(255) NOT NULL,
                  enrolled varchar(255) NOT NULL,
                  created_at timestamp,
                  updated_At timestamp
                )"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))


@app.route('/count')
@login_required
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]
    return "This page was accessed %d times." % count


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.register_blueprint(user_module)
