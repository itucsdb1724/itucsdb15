import datetime
import psycopg2 as dbapi2

from flask import current_app as app


class Course():
    # id serial PRIMARY KEY
    # course_code varchar(255) NOT NULL
    # title varchar(255) NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self, course_code=None, title=None):
        self.id = None
        self.course_code = course_code
        self.title = title
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    @classmethod
    def from_database(self, row):
        course = Course()
        course.id = row[0]
        course.course_code = row[1]
        course.title = row[2]
        course.created_at = row[3]
        course.updated_at = row[4]
        return course


class CourseConnection:

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
    def find_by_course_code(self, course_code):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM courses WHERE course_code = %s LIMIT 1"""
            cursor.execute(query, [course_code])
            data = cursor.fetchone()
            if data is None:
                return None
            return Course.from_database(data)

    @classmethod
    def create(self, course):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO courses (course_code, title, created_at, updated_at)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id, course_code, title, created_at, updated_at"""
            cursor.execute(query, (course.course_code, course.title, course.created_at, course.updated_at))
            connection.commit()
            course = Course.from_database(cursor.fetchone())
            return course
