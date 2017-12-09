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
from app.teacher.controllers import teacher as teacher_module
from app.course.controllers import course as course_module
from app.section.controllers import section as section_module
from app.file.controllers import file as file_module

from app.user.models import User, UserRepository
from app.teacher.models import Teacher, TeacherRepository
from app.course.models import Course, CourseRepository
from app.section.models import Section, SectionRepository
from app.grade.models import Grade, GradeRepository

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'


app.config['APP_ROOT'] = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_DIR'] = os.path.join(app.config['APP_ROOT'], 'static', 'uploads')

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(session_token):
    return UserRepository.find_by_session_token(session_token)


@app.route('/')
def home_page():
    courses = CourseRepository.find_recents(5)
    sections = SectionRepository.find_recents(5)
    teachers = TeacherRepository.find_recents(5)
    return render_template('home.html', sections=sections, courses=courses, teachers=teachers)


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS users CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE  users (
                  id serial PRIMARY KEY,
                  email varchar(255) NOT NULL,
                  username varchar(255) NOT NULL,
                  password varchar(255) NOT NULL,
                  session_token varchar(255) NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS courses CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE courses (
                  id serial PRIMARY KEY,
                  department_code varchar(3) NOT NULL,
                  course_code varchar(5) NOT NULL,
                  title varchar(255) NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS teachers CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE teachers (
                  id serial PRIMARY KEY,
                  name varchar(255) NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS sections CASCADE"""
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
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS grades CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE grades (
                  id serial PRIMARY KEY,
                  course_id integer REFERENCES courses ON DELETE SET NULL ON UPDATE CASCADE,
                  teacher_id integer REFERENCES teachers  ON DELETE SET NULL ON UPDATE CASCADE,
                  user_id integer REFERENCES users  ON DELETE SET NULL ON UPDATE CASCADE,
                  filename varchar(255) NOT NULL,
                  AA_count integer NOT NULL,
                  BA_count integer NOT NULL,
                  BB_count integer NOT NULL,
                  CB_count integer NOT NULL,
                  CC_count integer NOT NULL,
                  DC_count integer NOT NULL,
                  DD_count integer NOT NULL,
                  FF_count integer NOT NULL,
                  VF_count integer NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)


        query = """DROP TABLE IF EXISTS messages CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE messages (
                  id serial PRIMARY KEY,
                  thread_id integer REFERENCES messages ON DELETE CASCADE ON UPDATE CASCADE,
                  user_id integer REFERENCES users ON DELETE CASCADE ON UPDATE CASCADE,
                  course_id integer REFERENCES courses ON DELETE SET NULL ON UPDATE CASCADE,
                  section_id integer REFERENCES sections ON DELETE SET NULL ON UPDATE CASCADE,
                  section_only boolean NOT NULL DEFAULT false,
                  title varchar(255) NOT NULL,
                  message varchar(1000) NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS files"""
        cursor.execute(query)

        query = """CREATE TABLE files (
                  id serial PRIMARY KEY,
                  course_id integer REFERENCES courses ON DELETE SET NULL ON UPDATE CASCADE,
                  section_id integer REFERENCES sections ON DELETE SET NULL ON UPDATE CASCADE,
                  user_id integer REFERENCES users ON DELETE SET NULL ON UPDATE CASCADE,
                  section_only boolean NOT NULL DEFAULT false,
                  title varchar(255) NOT NULL,
                  filename varchar(255) NOT NULL,
                  original_filename varchar(255) NOT NULL,
                  content_type varchar(255) NOT NULL,
                  created_at timestamp NOT NULL,
                  updated_At timestamp NOT NULL
                )"""
        cursor.execute(query)

        connection.commit()


    teacher1 = TeacherRepository.create(Teacher("Feanor"))
    teacher2 = TeacherRepository.create(Teacher("Hayri"))
    teacher3 = TeacherRepository.create(Teacher("Turgut"))
    teacher4 = TeacherRepository.create(Teacher("Uyar"))
    teacher5 = TeacherRepository.create(Teacher("Ahmet"))
    teacher6 = TeacherRepository.create(Teacher("Sabih"))
    teacher7 = TeacherRepository.create(Teacher("Atadan"))
    course1 = CourseRepository.create(Course("BLG", "313", "Giris"))
    course2 = CourseRepository.create(Course("BLG", "312", "Cikis"))
    course3 = CourseRepository.create(Course("TAR", "314", "Basl"))
    course4 = CourseRepository.create(Course("SAN", "315", "Hell"))
    course5 = CourseRepository.create(Course("ALT", "316", "Silmaril"))
    course6 = CourseRepository.create(Course("SIL", "317", "Mellon"))
    course7 = CourseRepository.create(Course("TRF", "318", "Ungolianth"))

    section = Section()
    section.crn = 31228
    section.building = "EEB"
    section.day = "monday"
    section.time = "morning"
    section.room = "d212"
    section.capacity = 21
    section.enrolled = 12


    section.crn = 12373
    section.course_id =course1.id
    section.teacher_id = teacher1.id
    SectionRepository.create(section)

    section.crn = 67537
    section.course_id =course1.id
    section.teacher_id = teacher2.id
    SectionRepository.create(section)

    section.crn = 23675
    section.course_id =course2.id
    section.teacher_id = teacher3.id
    SectionRepository.create(section)

    section.crn = 82847
    section.course_id =course3.id
    section.teacher_id = teacher4.id
    SectionRepository.create(section)

    section.crn = 72639
    section.course_id =course3.id
    section.teacher_id = teacher1.id
    SectionRepository.create(section)

    section.crn = 23379
    section.course_id =course4.id
    section.teacher_id = teacher5.id
    SectionRepository.create(section)

    section.crn = 97357
    section.course_id =course6.id
    section.teacher_id = teacher7.id
    SectionRepository.create(section)

    section.crn = 22134
    section.course_id =course7.id
    section.teacher_id = teacher3.id
    SectionRepository.create(section)

    section.crn = 23380
    section.course_id =course2.id
    section.teacher_id = teacher7.id
    SectionRepository.create(section)

    section.crn = 97761
    section.course_id =course6.id
    section.teacher_id = teacher2.id
    SectionRepository.create(section)

    return redirect(url_for('home_page'))


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.register_blueprint(user_module)
app.register_blueprint(teacher_module)
app.register_blueprint(course_module)
app.register_blueprint(section_module)
app.register_blueprint(file_module)
