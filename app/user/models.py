import datetime
import psycopg2 as dbapi2
import string
import random

from flask import current_app as app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    # id serial PRIMARY KEY
    # email varchar(255) NOT NULL
    # username varchar(255) NOT NULL
    # password_hash varchar(255) NOT NULL
    # session_token varchar(255) NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self, username=None, email=None):
        self.id = None
        self.username = username
        self.email = email
        self.password_hash = None
        self.session_token = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(32))
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def from_database(self, row):
        user = User()
        user.id = row[0]
        user.username = row[1]
        user.email = row[2]
        user.password_hash = row[3]
        user.session_token = row[4]
        user.created_at = row[5]
        user.updated_at = row[6]
        return user


class UserConnection:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM users WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return User.from_database(data)

    def find_by_email(email):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM users WHERE email = %s LIMIT 1"""
            cursor.execute(query, [email])
            data = cursor.fetchone()
            if data is None:
                return None
            return User.from_database(data)

    def find_by_session_token(session_token):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM users WHERE session_token = %s LIMIT 1"""
            cursor.execute(query, [session_token])
            data = cursor.fetchone()
            if data is None:
                return None
            return User.from_database(data)

    @classmethod
    def create(self, user):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO users (username, email, password, session_token, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id, username, email, password, session_token, created_at, updated_at"""
            cursor.execute(query, (user.username, user.email, user.password_hash,
                                   user.session_token, user.created_at, user.updated_at))
            connection.commit()
            user = User.from_database(cursor.fetchone())
            return user
