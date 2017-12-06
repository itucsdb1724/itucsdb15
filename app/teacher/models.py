import datetime
import psycopg2 as dbapi2

from flask import current_app as app


class Teacher():
    # id serial PRIMARY KEY
    # name varchar(255) NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self, name=None):
        self.id = None
        self.name = name
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    @classmethod
    def from_database(self, row):
        teacher = Teacher()
        teacher.id = row[0]
        teacher.name = row[1]
        teacher.created_at = row[2]
        teacher.updated_at = row[3]
        return teacher


class TeacherRepository:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM teachers WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Teacher.from_database(data)

    @classmethod
    def create(self, teacher):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO teachers (name, created_at, updated_at)
                            VALUES (%s, %s, %s)
                            RETURNING id, name, created_at, updated_at"""
            cursor.execute(query, (teacher.name, teacher.created_at, teacher.updated_at))
            connection.commit()
            teacher = Teacher.from_database(cursor.fetchone())
            return teacher
