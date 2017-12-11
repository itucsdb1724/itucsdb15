import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.course.models import Course, CourseRepository
from app.section.models import SectionRepository
from app.user.models import User, UserRepository


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

        # relations
        self.course = None
        self.section = None
        self.user = None
        self.thread = None

    def get_course(self):
        if self.course is None:
            self.course = CourseRepository.find_by_id(self.course_id)
        return self.course

    def get_section(self):
        if self.section is None:
            self.section = SectionRepository.find_by_id(self.section_id)
        return self.section

    def get_user(self):
        if self.user is None:
            self.user = UserRepository.find_by_id(self.user_id)
        return self.user

    def get_thread(self):
        if self.thread is None:
            self.thread = MessageRepository.find_by_id(self.thread_id)
        return self.thread

    def message_count(self):
        return MessageRepository.message_count(self.id) + 1

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
            query = """SELECT m.id, m.thread_id, m.user_id, m.course_id, m.section_id, m.section_only, m.title, m.message, m.created_at, m.updated_at,
                              u.id, u.email, u.username, u.password, u.session_token, u.created_at, u.updated_at FROM messages AS m INNER JOIN users AS u ON m.user_id = u.id WHERE section_id = %s AND thread_id is NULL ORDER BY m.created_at"""
            cursor.execute(query, [section_id])
            data = cursor.fetchall()
            def parse_database_row(row):
                message = Message.from_database(row[0:10])
                message.user = User.from_database(row[10:17])
                return message
            return list(map(parse_database_row, data))

    @classmethod
    def find_threads_of_course(self, course_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT m.id, m.thread_id, m.user_id, m.course_id, m.section_id, m.section_only, m.title, m.message, m.created_at, m.updated_at,
                              u.id, u.email, u.username, u.password, u.session_token, u.created_at, u.updated_at FROM messages AS m INNER JOIN users AS u ON m.user_id = u.id WHERE m.course_id = %s AND m.section_only = false AND m.thread_id is NULL ORDER BY m.created_at"""
            cursor.execute(query, [course_id])
            data = cursor.fetchall()
            def parse_database_row(row):
                message = Message.from_database(row[0:10])
                message.user = User.from_database(row[10:17])
                return message
            return list(map(parse_database_row, data))

    @classmethod
    def find_messages_of_thread(self, thread_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT m.id, m.thread_id, m.user_id, m.course_id, m.section_id, m.section_only, m.title, m.message, m.created_at, m.updated_at,
                              u.id, u.email, u.username, u.password, u.session_token, u.created_at, u.updated_at FROM messages AS m INNER JOIN users AS u ON m.user_id = u.id WHERE m.thread_id = %s OR m.id = %s ORDER BY m.created_at"""
            cursor.execute(query, [thread_id, thread_id])
            data = cursor.fetchall()
            def parse_database_row(row):
                message = Message.from_database(row[0:10])
                message.user = User.from_database(row[10:17])
                return message
            return list(map(parse_database_row, data))

    @classmethod
    def find_messages_of_user(self, user_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                query = """SELECT m.id, m.thread_id, m.user_id, m.course_id, m.section_id, m.section_only, m.title, m.message, m.created_at, m.updated_at,
                                  c.id, c.department_code, c.course_code, c.title, c.created_at, c.updated_At FROM messages AS m INNER JOIN courses AS c ON m.course_id = c.id WHERE m.user_id = %s ORDER BY m.created_at"""
                cursor.execute(query, [user_id])
                def parse_database_row(row):
                    message = Message.from_database(row[0:10])
                    message.course = Course.from_database(row[10:16])
                    return message
                return list(map(parse_database_row, cursor.fetchall()))

    @classmethod
    def update_section_only(self, id, section_only):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE messages SET section_only = %s WHERE id = %s OR thread_id = %s"""
            cursor.execute(query, [section_only, id, id])
            cursor.close()
            return True

    @classmethod
    def message_count(self, thread_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                query = """SELECT count(*) FROM messages WHERE thread_id = %s"""
                cursor.execute(query, [thread_id])
                return cursor.fetchone()[0]

    @classmethod
    def delete(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM messages WHERE id = %s"""
            cursor.execute(query, [id])
            cursor.close()
            return True

    @classmethod
    def create(self, message):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO messages (thread_id, user_id, course_id, section_id, section_only, title, message, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, thread_id, user_id, course_id, section_id, section_only, title, message, created_at, updated_at"""
            cursor.execute(query, (message.thread_id, message.user_id, message.course_id, message.section_id,
                                   message.section_only, message.title, message.message, message.created_at, message.updated_at))
            connection.commit()
            message = Message.from_database(cursor.fetchone())
            return message
