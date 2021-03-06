import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.connection import get_connection
from app.course.models import CourseRepository
from app.teacher.models import TeacherRepository

class Section():
    # id serial PRIMARY KEY
    # course_id integer REFERENCES courses
    # teacher_id integer REFERENCES teachers
    # crn integer NOT NULL
    # building varchar(255)
    # day varchar(255) NOT NULL
    # time varchar(255) NOT NULL
    # room varchar(255)
    # capacity integer NOT NULL
    # enrolled integer NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self):
        self.id = None
        self.course_id = None
        self.teacher_id = None
        self.crn = None
        self.building = None
        self.day = None
        self.time = None
        self.room = None
        self.capacity = None
        self.enrolled = None
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

        # relations
        self.course = None
        self.teacher = None


    def get_course(self):
        if self.course is None:
            self.course = CourseRepository.find_by_id(self.course_id)
        return self.course


    def get_teacher(self):
        if self.teacher is None:
            self.teacher = TeacherRepository.find_by_id(self.teacher_id)
        return self.teacher

    @classmethod
    def from_database(self, row):
        section = Section()
        section.id = row[0]
        section.course_id = row[1]
        section.teacher_id = row[2]
        section.crn = row[3]
        section.building = row[4]
        section.day = row[5]
        section.time = row[6]
        section.room = row[7]
        section.capacity = row[8]
        section.enrolled = row[9]
        section.created_at = row[10]
        section.updated_at = row[11]
        return section


class SectionRepository:

    @classmethod
    def find_by_id(self, id):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM sections WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Section.from_database(data)


    @classmethod
    def all(self):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM sections"""
            cursor.execute(query)
            def parse_database_row(row): return Section.from_database(row)
            return list(map(parse_database_row, cursor.fetchall()))


    @classmethod
    def find_random(self, limit = 0):
        with get_connection().cursor() as cursor:
            if limit > 0:
                query = """SELECT * FROM sections ORDER BY capacity DESC OFFSET random() * (SELECT count(*) FROM sections) LIMIT %s"""
                cursor.execute(query, [limit])
            else:
                query = """SELECT * FROM sections ORDER BY capacity DESC OFFSET random() * (SELECT count(*) FROM sections)"""
                cursor.execute(query)
            data = cursor.fetchall()
            def parse_database_row(row): return Section.from_database(row)
            return list(map(parse_database_row, data))


    @classmethod
    def find_sections_of_teacher(self, teacher_id):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM sections WHERE teacher_id = %s ORDER BY created_at"""
            cursor.execute(query, [teacher_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Section.from_database(row)
            return list(map(parse_database_row, data))


    @classmethod
    def find_sections_of_course(self, course_id):
        with get_connection().cursor() as cursor:
            query = """SELECT * FROM sections WHERE course_id = %s ORDER BY created_at"""
            cursor.execute(query, [course_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Section.from_database(row)
            return list(map(parse_database_row, data))


    @classmethod
    def create(self, section):
        with get_connection().cursor() as cursor:
            now = datetime.datetime.now()
            query = """INSERT INTO sections (course_id, teacher_id, crn, building, day, time, room, capacity, enrolled, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, course_id, teacher_id, crn, building, day, time, room, capacity, enrolled, created_at, updated_at"""
            cursor.execute(query, (section.course_id, section.teacher_id, section.crn, section.building, section.day, section.time, section.room, section.capacity, section.enrolled, section.created_at, section.updated_at))
            get_connection().commit()
            section = Section.from_database(cursor.fetchone())
            return section
