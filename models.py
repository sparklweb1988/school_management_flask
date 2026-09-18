from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


# =========================================================
# USER
# =========================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="student"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="user",
        uselist=False
    )

    student = db.relationship(
        "Student",
        back_populates="user",
        uselist=False
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


# =========================================================
# SCHOOL SESSION
# =========================================================

class SchoolSession(db.Model):

    __tablename__ = "school_sessions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    year = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    results = db.relationship(
        "Result",
        back_populates="session"
    )


# =========================================================
# TERM
# =========================================================

class Term(db.Model):

    __tablename__ = "terms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    results = db.relationship(
        "Result",
        back_populates="term"
    )


# =========================================================
# CLASSROOM
# =========================================================

class Classroom(db.Model):

    __tablename__ = "classrooms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    students = db.relationship(
        "Student",
        back_populates="classroom"
    )

    teacher_assignments = db.relationship(
        "TeacherAssignment",
        back_populates="classroom",
        cascade="all, delete-orphan"
    )

    results = db.relationship(
        "Result",
        back_populates="classroom"
    )


# =========================================================
# SUBJECT
# =========================================================

class Subject(db.Model):

    __tablename__ = "subjects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    teacher_assignments = db.relationship(
        "TeacherAssignment",
        back_populates="subject",
        cascade="all, delete-orphan"
    )

    results = db.relationship(
        "Result",
        back_populates="subject"
    )


# =========================================================
# TEACHER
# =========================================================

class Teacher(db.Model):

    __tablename__ = "teachers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(30)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    user = db.relationship(
        "User",
        back_populates="teacher"
    )

    assignments = db.relationship(
        "TeacherAssignment",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )


# =========================================================
# STUDENT
# =========================================================

class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    parent_name = db.Column(
        db.String(150)
    )

    age = db.Column(
        db.Integer
    )

    phone = db.Column(
        db.String(30)
    )

    classroom_id = db.Column(
        db.Integer,
        db.ForeignKey("classrooms.id"),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    user = db.relationship(
        "User",
        back_populates="student"
    )

    classroom = db.relationship(
        "Classroom",
        back_populates="students"
    )

    results = db.relationship(
        "Result",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# =========================================================
# TEACHER ASSIGNMENT
# =========================================================

class TeacherAssignment(db.Model):

    __tablename__ = "teacher_assignments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teachers.id"),
        nullable=False
    )

    classroom_id = db.Column(
        db.Integer,
        db.ForeignKey("classrooms.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="assignments"
    )

    classroom = db.relationship(
        "Classroom",
        back_populates="teacher_assignments"
    )

    subject = db.relationship(
        "Subject",
        back_populates="teacher_assignments"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "teacher_id",
            "classroom_id",
            "subject_id",
            name="unique_teacher_class_subject"
        ),
    )


# =========================================================
# RESULT
# =========================================================

class Result(db.Model):

    __tablename__ = "results"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    classroom_id = db.Column(
        db.Integer,
        db.ForeignKey("classrooms.id"),
        nullable=False
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("school_sessions.id"),
        nullable=False
    )

    term_id = db.Column(
        db.Integer,
        db.ForeignKey("terms.id"),
        nullable=False
    )

    ca_score = db.Column(
        db.Float,
        default=0
    )

    exam_score = db.Column(
        db.Float,
        default=0
    )

    student = db.relationship(
        "Student",
        back_populates="results"
    )

    subject = db.relationship(
        "Subject",
        back_populates="results"
    )

    classroom = db.relationship(
        "Classroom",
        back_populates="results"
    )

    session = db.relationship(
        "SchoolSession",
        back_populates="results"
    )

    term = db.relationship(
        "Term",
        back_populates="results"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "subject_id",
            "session_id",
            "term_id",
            name="unique_student_subject_session_term"
        ),
    )

    @property
    def total_score(self):

        return (
            self.ca_score +
            self.exam_score
        )