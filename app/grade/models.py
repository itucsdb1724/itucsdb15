import datetime
import psycopg2 as dbapi2

from flask import current_app as app

from app.teacher.models import TeacherRepository
from app.course.models import CourseRepository


class Grade():
    # id serial PRIMARY KEY
    # course_id integer REFERENCES courses NOT NULL
    # teacher_id integer REFERENCES teachers NOT NULL
    # filename varchar(255) NOT NULL
    # AA_count integer NOT NULL
    # BA_count integer NOT NULL
    # BB_count integer NOT NULL
    # CB_count integer NOT NULL
    # CC_count integer NOT NULL
    # DC_count integer NOT NULL
    # DD_count integer NOT NULL
    # FF_count integer NOT NULL
    # VF_count integer NOT NULL
    # created_at timestamp
    # updated_At timestamp

    def __init__(self):
        self.id = None
        self.course_id = None
        self.teacher_id = None
        self.filename = None
        self.AA_count = None
        self.BA_count = None
        self.BB_count = None
        self.CB_count = None
        self.CC_count = None
        self.DC_count = None
        self.DD_count = None
        self.FF_count = None
        self.VF_count = None
        now = datetime.datetime.now()
        self.created_at = now.ctime()
        self.updated_at = now.ctime()

    def teacher(self):
        return TeacherRepository.find_by_id(self.teacher_id)

    def course(self):
        return CourseRepository.find_by_id(self.course_id)


    @classmethod
    def from_database(self, row):
        grade = Grade()
        grade.id = row[0]
        grade.course_id = row[1]
        grade.teacher_id = row[2]
        grade.filename = row[3]
        grade.AA_count = row[4]
        grade.BA_count = row[5]
        grade.BB_count = row[6]
        grade.CB_count = row[7]
        grade.CC_count = row[8]
        grade.DC_count = row[9]
        grade.DD_count = row[10]
        grade.FF_count = row[11]
        grade.VF_count = row[12]
        grade.created_at = row[13]
        grade.updated_at = row[14]
        return grade


class GradeRepository:

    @classmethod
    def find_by_id(self, id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM grades WHERE id = %s LIMIT 1"""
            cursor.execute(query, [id])
            data = cursor.fetchone()
            if data is None:
                return None
            return Grade.from_database(data)

    @classmethod
    def find_grades_of_teacher(self, teacher_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM grades WHERE teacher_id = %s"""
            cursor.execute(query, [teacher_id])
            data = cursor.fetchall()
            def parse_database_row(row): return Grade.from_database(row)
            return list(map(parse_database_row, data))

    @classmethod
    def create(self, grade):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            now = datetime.datetime.now()
            query = """INSERT INTO grades (course_id, teacher_id, filename, AA_count, BA_count, BB_count, CB_count, CC_count, DC_count, DD_count, FF_count, VF_count, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, course_id, teacher_id, filename, AA_count, BA_count, BB_count, CB_count, CC_count, DC_count, DD_count, FF_count, VF_count, created_at, updated_at"""
            cursor.execute(query, (grade.course_id, grade.teacher_id, grade.filename, grade.AA_count, grade.BA_count, grade.BB_count, grade.CB_count, grade.CC_count, grade.DC_count, grade.DD_count, grade.FF_count, grade.VF_count, grade.created_at, grade.updated_at))
            connection.commit()
            grade = Grade.from_database(cursor.fetchone())
            # TODO: close cursor or find better solution
            return grade

