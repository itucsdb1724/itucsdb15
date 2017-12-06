import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.course.models import CourseRepository
from app.section.models import SectionRepository
from app.user.models import UserRepository


class File():
    # id serial PRIMARY KEY,
    # course_id integer REFERENCES courses
    # section_id integer REFERENCES sections
    # user_id integer REFERENCES users
    # section_only boolean
    # file_name varchar(255)
    # file_size varchar(255)
    # file_ext varchar(255)
    # created_at timestamp
    # updated_At timestamp

    def __init__(self):
        self.id = None
        self.course_id = None
        self.section_id = None
        self.user_id = None
        self.section_only = False
        self.file_name = None
        self.file_size = None
        self.file_ext = None
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    def course(self):
        return CourseRepository.find_by_id(self.course_id)

    def section(self):
        return SectionRepository.find_by_id(self.section_id)

    def user(self):
        return UserRepository.find_by_id(self.user_id)

    @classmethod
    def from_database(self, row):
        file = File()
        file.id = row[0]
        file.course_id = row[1]
        file.section_id = row[2]
        file.user_id = row[3]
        file.section_only = row[4]
        file.file_name = row[5]
        file.file_size = row[6]
        file.file_ext = row[7]
        file.created_at = row[8]
        file.updated_at = row[9]
        return file


class FileRepository:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM files WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return File.from_database(data)

    @classmethod
    def find_files_of_section(self, section_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM files WHERE section_id = %s AND file_id = NULL ORDER BY created_at"""
            cursor.execute(query, [section_id])
            data = cursor.fetchall()
            def parse_database_row(row): return File.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def find_files_of_class(self, class_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM files WHERE class_id = %s AND section_only = false AND file_id = NULL ORDER BY created_at"""
            cursor.execute(query, [class_id])
            data = cursor.fetchall()
            def parse_database_row(row): return File.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def create(self, section):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO files (course_id, section_id, user_id, section_only, file_name, file_size, file_ext, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, course_id, section_id, user_id, section_only, file_name, file_size, file_ext, created_at, updated_at"""
            cursor.execute(query, (file.course_id, file.section_id, file.user_id,
                                   file.section_only, file.file_name, file.file_size, file.file_ext, file.created_at, file.updated_at))
            connection.commit()
            section = parse_database_row(cursor.fetchone())
            return section
