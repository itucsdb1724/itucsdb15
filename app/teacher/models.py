import datetime
import psycopg2 as dbapi2

from flask import current_app as app
from app.connection import get_connection

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
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM teachers WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Teacher.from_database(data)

    @classmethod
    def find_by_name(self, name):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM teachers WHERE name = %s LIMIT 1"""
            cursor.execute(query, [name])
            data = cursor.fetchone()
            if data is None:
                return None
            return Teacher.from_database(data)


    @classmethod
    def find_random(self, limit = 0):
        with get_connection().cursor() as cursor:
            if limit > 0:
                query = """SELECT * FROM teachers OFFSET random() * (SELECT count(*) FROM teachers) LIMIT %s"""
                cursor.execute(query, [limit])
            else:
                query = """SELECT * FROM teachers OFFSET random() * (SELECT count(*) FROM teachers)"""
                cursor.execute(query)
            data = cursor.fetchall()
            def parse_database_row(row): return Teacher.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def find_recents(self, limit = 0):
        with get_connection().cursor() as cursor:
            if limit > 0:
                query = """SELECT * FROM teachers ORDER BY updated_at LIMIT %s"""
                cursor.execute(query, [limit])
            else:
                query = """SELECT * FROM teachers ORDER BY updated_at"""
                cursor.execute(query)
            data = cursor.fetchall()
            def parse_database_row(row): return Teacher.from_database(row)
            return list(map(parse_database_row, data))


    @classmethod
    def search(self, q):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM teachers WHERE UPPER(name) ILIKE %s"""
            cursor.execute(query, ['%'+ q.upper() +'%'])
            data = cursor.fetchall()
            def parse_database_row(row): return Teacher.from_database(row)
            return list(map(parse_database_row, data))


    @classmethod
    def create(self, teacher):
        with get_connection().cursor() as cursor:
            now = datetime.datetime.now()
            query = """INSERT INTO teachers (name, created_at, updated_at)
                            VALUES (%s, %s, %s)
                            RETURNING id, name, created_at, updated_at"""
            cursor.execute(query, (teacher.name, teacher.created_at, teacher.updated_at))
            get_connection().commit()
            teacher = Teacher.from_database(cursor.fetchone())
            return teacher
