import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.course.models import CourseRepository
from app.section.models import SectionRepository
from app.user.models import UserRepository


class Message():
    # id serial PRIMARY KEY,
    # thread_id integer REFERENCES messages
    # user_id integer REFERENCES users
    # course_id integer REFERENCES courses
    # section_id integer REFERENCES sections
    # section_only boolean
    # title varchar(255)
    # message varchar(1000)
    # created_at timestamp
    # updated_At timestamp

    def __init__(self):
        self.id = None
        self.thread_id = None
        self.user_id = None
        self.course_id = None
        self.section_id = None
        self.section_only = False
        self.title = None
        self.message = None
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
        message = Message()
        message.id = row[0]
        message.thread_id = row[1]
        message.user_id = row[2]
        message.course_id = row[3]
        message.section_id = row[4]
        message.section_only = row[5]
        message.title = row[6]
        message.message = row[7]
        message.created_at = row[8]
        message.updated_at = row[9]
        return message


class MessageRepository:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM messages WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Message.from_database(data)

    @classmethod
    def find_threads_of_section(self, section_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM messages WHERE section_id = %s AND thread_id = NULL ORDER BY created_at"""
            cursor.execute(query, [section_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Message.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def find_threads_of_class(self, class_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM messages WHERE class_id = %s AND section_only = false AND thread_id = NULL ORDER BY created_at"""
            cursor.execute(query, [class_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Message.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def find_messages_of_thread(self, thread_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM messages WHERE thread_id = %s OR id = %s ORDER BY created_at"""
            cursor.execute(query, [thread_id, thread_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Message.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def create(self, section):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO messages (thread_id, user_id, course_id, section_id, section_only, title, message, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, thread_id, user_id, course_id, section_id, section_only, title, message, created_at, updated_at"""
            cursor.execute(query, (message.thread_id, message.user_id, message.course_id, message.section_id,
                                   message.section_only, message.title, message.message, message.created_at, message.updated_at))
            connection.commit()
            section = parse_database_row(cursor.fetchone())
            return section
