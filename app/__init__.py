import datetime
import json
import os
import psycopg2 as dbapi2
import re
from lxml import html
import requests

from flask import Flask, redirect, render_template, g
from flask.helpers import url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required

from app.connection import get_connection

from app.user.controllers import user as user_module
from app.teacher.controllers import teacher as teacher_module
from app.course.controllers import course as course_module
from app.section.controllers import section as section_module
from app.file.controllers import file as file_module
from app.message.controllers import message as message_module

from app.user.models import User, UserRepository
from app.teacher.models import Teacher, TeacherRepository
from app.course.models import Course, CourseRepository
from app.section.models import Section, SectionRepository

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
    department_codes = CourseRepository.find_department_codes()
    return render_template('home.html', sections=sections, courses=courses, teachers=teachers, department_codes=department_codes)


@app.route('/initdb')
def initialize_database():
    with get_connection().cursor() as cursor:
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

        get_connection().commit()
    return redirect(url_for('home_page'))

@app.route('/parse_itu')
def parse_itu():
    page = requests.get('http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php')
    tree = html.fromstring(page.content)

    #This will create a list of course_codes
    course_codes = tree.xpath('//select[@name="bolum"]/option[not(@selected)]/text()')

    # print 'Course Codes: '
    for course_code in course_codes:
        link = 'http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php?fb=' + course_code
        page = requests.get(link.strip())
        tree = html.fromstring(page.content)
        tds = tree.xpath('//table[@class="dersprg"]/tr[@onmouseover]/td')
        courses = []
        while len(tds) > 14:
            pice = tds[:14]
            courses.append(pice)
            tds   = tds[14:]
        courses.append(tds)

        if len(courses[0]) == 0:
            continue

        sections = []
        for course in courses:
            course_sections = [{}]
            course_sections[0]['crn'] = course[0].text
            course_sections[0]['course_code'] = course[1].getchildren()[0].text
            course_sections[0]['title'] = course[2].text
            course_sections[0]['instructor'] = course[3].text
            course_sections[0]['capacity'] = course[8].text
            course_sections[0]['enrolled'] = course[9].text


            buildings = course[4].text_content()
            days = list(filter(None, course[5].text_content().split(' ')))
            hours = list(filter(None, course[6].text_content().split(' ')))


            if len(course[7].text_content().strip()) == 0:
                classes_content = "---"
            else:
                classes_content = course[7].text_content()

            classes = list(filter(None, classes_content.split(' ')))

            sections_count = len(buildings) // 3

            for x in range(0,sections_count):
                if x >= len(course_sections):
                    course_sections.append(course_sections[x-1].copy())
                course_section = course_sections[x]
                course_section['building'] = buildings[(x * 3): ((x + 1) * 3)]
                course_section['day'] = days[x]
                course_section['hour'] = hours[x]
                course_section['class'] = classes[x]

            for data in course_sections:
                course_codes = data['course_code'].split(' ')

                course = CourseRepository.find_by_department_and_course_code(course_codes[0], course_codes[1])
                if not course:
                    course = CourseRepository.create(Course(course_codes[0], course_codes[1], data['title']))

                instructor = data['instructor'].split(',')[0]
                teacher = TeacherRepository.find_by_name(instructor)
                if not teacher:
                    teacher = TeacherRepository.create(Teacher(instructor))

                section = Section()
                section.crn = int(data['crn'])
                section.building = data['building']
                section.day = data['day']
                section.time = data['hour']
                section.room = data['class']
                section.capacity = data['capacity']
                section.enrolled = data['enrolled']
                section.course_id = course.id
                section.teacher_id = teacher.id
                SectionRepository.create(section)

    return redirect(url_for('home_page'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.teardown_appcontext
def close_connection(error):
    if hasattr(g, 'connection'):
        g.connection.close()

app.register_blueprint(user_module)
app.register_blueprint(teacher_module)
app.register_blueprint(course_module)
app.register_blueprint(section_module)
app.register_blueprint(file_module)
app.register_blueprint(message_module)
