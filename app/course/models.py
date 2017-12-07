import datetime
import psycopg2 as dbapi2

from flask import current_app as app


class Course():
    # id serial PRIMARY KEY
    # department_code varchar(3) NOT NULL
    # course_code varchar(5) NOT NULL
    # title varchar(255) NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self, department_code=None, course_code=None, title=None):
        self.id = None
        self.department_code = department_code
        self.course_code = course_code
        self.title = title
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    @classmethod
    def from_database(self, row):
        course = Course()
        course.id = row[0]
        course.department_code = row[1]
        course.course_code = row[2]
        course.title = row[3]
        course.created_at = row[4]
        course.updated_at = row[5]
        return course


class CourseRepository:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM courses WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Course.from_database(data)

    @classmethod
    def find_by_department_and_course_code(self, department_code, course_code):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM courses WHERE department_code = %s AND course_code = %s LIMIT 1"""
            cursor.execute(query, [department_code, course_code])
            data = cursor.fetchone()
            if data is None:
                return None
            return Course.from_database(data)

    @classmethod
    def create(self, course):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO courses (department_code, course_code, title, created_at, updated_at)
                            VALUES (%s %s, %s, %s, %s)
                            RETURNING id, department_code, course_code, title, created_at, updated_at"""
            cursor.execute(query, (course.department_code, course.course_code, course.title, course.created_at, course.updated_at))
            connection.commit()
            course = Course.from_database(cursor.fetchone())
            return course
