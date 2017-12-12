import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.connection import get_connection
from app.course.models import Course, CourseRepository
from app.section.models import SectionRepository
from app.user.models import User, UserRepository


class File():
    # id serial PRIMARY KEY,
    # course_id integer REFERENCES courses
    # section_id integer REFERENCES sections
    # user_id integer REFERENCES users
    # section_only boolean
    # title varchar(255)
    # filename varchar(255)
    # original_filename varchar(255)
    # content_type varchar(255)
    # created_at timestamp
    # updated_At timestamp

    def __init__(self):
        self.id = None
        self.course_id = None
        self.section_id = None
        self.user_id = None
        self.section_only = False
        self.title = None
        self.filename = None
        self.original_filename = None
        self.content_type = None
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

        # relations
        self.course = None
        self.section = None
        self.user = None

    def course(self):
        if self.course is None:
            self.course = CourseRepository.find_by_id(self.course_id)
        return self.course

    def section(self):
        if self.section is None:
            self.section = SectionRepository.find_by_id(self.section_id)
        return self.section

    def user(self):
        if self.user is None:
            self.user = UserRepository.find_by_id(self.user_id)
        return self.user

    @classmethod
    def from_database(self, row):
        file = File()
        file.id = row[0]
        file.course_id = row[1]
        file.section_id = row[2]
        file.user_id = row[3]
        file.section_only = row[4]
        file.title = row[5]
        file.filename = row[6]
        file.original_filename = row[7]
        file.content_type = row[8]
        file.created_at = row[9]
        file.updated_at = row[10]
        return file


class FileRepository:

    @classmethod
    def find_by_id(self, id):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM files WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return File.from_database(data)

    @classmethod
    def find_files_of_section(self, section_id):
        with get_connection().cursor() as cursor:
            query = """SELECT f.id, f.course_id, f.section_id, f.user_id, f.section_only, f.title, f.filename, f.original_filename, f.content_type, f.created_at, f.updated_at,
                              u.id, u.email, u.username, u.password, u.session_token, u.created_at, u.updated_at FROM files AS f INNER JOIN users AS u ON f.user_id = u.id WHERE f.section_id = %s ORDER BY f.created_at"""
            cursor.execute(query, [section_id])
            data = cursor.fetchall()
            def parse_database_row(row):
                file = File.from_database(row[0:11])
                file.user = User.from_database(row[11:18])
                return file
            return list(map(parse_database_row, data))


    @classmethod
    def find_files_of_course(self, course_id):
        with get_connection().cursor() as cursor:
            query = """SELECT f.id, f.course_id, f.section_id, f.user_id, f.section_only, f.title, f.filename, f.original_filename, f.content_type, f.created_at, f.updated_at,
                              u.id, u.email, u.username, u.password, u.session_token, u.created_at, u.updated_at FROM files AS f INNER JOIN users AS u ON f.user_id = u.id WHERE f.course_id = %s ORDER BY f.created_at"""
            cursor.execute(query, [course_id])
            data = cursor.fetchall()
            def parse_database_row(row):
                file = File.from_database(row[0:11])
                file.user = User.from_database(row[11:18])
                return file
            return list(map(parse_database_row, data))

    @classmethod
    def find_files_of_user(self, user_id):
        with get_connection().cursor() as cursor:
            query = """SELECT f.id, f.course_id, f.section_id, f.user_id, f.section_only, f.title, f.filename, f.original_filename, f.content_type, f.created_at, f.updated_at,
                              c.id, c.department_code, c.course_code, c.title, c.created_at, c.updated_At FROM files AS f INNER JOIN courses AS c ON f.course_id = c.id WHERE f.user_id = %s ORDER BY f.created_at"""
            cursor.execute(query, [user_id])
            def parse_database_row(row):
                file = File.from_database(row[0:11])
                file.course = Course.from_database(row[11:17])
                return file
            return list(map(parse_database_row, cursor.fetchall()))

    @classmethod
    def search(self, q):
        with get_connection().cursor() as cursor:
            query = """SELECT f.id, f.course_id, f.section_id, f.user_id, f.section_only, f.title, f.filename, f.original_filename, f.content_type, f.created_at, f.updated_at,
                              c.id, c.department_code, c.course_code, c.title, c.created_at, c.updated_At FROM files AS f INNER JOIN courses AS c ON f.course_id = c.id WHERE UPPER(f.title) ILIKE %s"""
            cursor.execute(query, ['%'+ q.upper() +'%'])
            def parse_database_row(row):
                file = File.from_database(row[0:11])
                file.course = Course.from_database(row[11:17])
                return file
            return list(map(parse_database_row, cursor.fetchall()))

    @classmethod
    def update_section_only(self, id, section_only):
        with get_connection().cursor() as cursor:
            query = """UPDATE files SET section_only = %s WHERE id = %s"""
            cursor.execute(query, [section_only, id])
            get_connection().commit()
            return True

    @classmethod
    def delete(self, id):
        with get_connection().cursor() as cursor:
            query = """DELETE FROM files WHERE id = %s"""
            try:
                cursor.execute(query, [id])
                get_connection().commit()
                return True
            except:
                return False

    @classmethod
    def create(self, file):
        with get_connection().cursor() as cursor:
            now = datetime.datetime.now()
            query = """INSERT INTO files (course_id, section_id, user_id, section_only, title, filename, original_filename, content_type, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, course_id, section_id, user_id, section_only, title, filename, original_filename, content_type, created_at, updated_at"""
            cursor.execute(query, (file.course_id, file.section_id, file.user_id,
                                   file.section_only, file.title, file.filename, file.original_filename, file.content_type, file.created_at, file.updated_at))
            get_connection().commit()
            file = File.from_database(cursor.fetchone())
            return file
