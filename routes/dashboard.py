from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import (
    Student,
    Teacher,
    Classroom,
    Subject,
    SchoolSession,
    Term,
    TeacherAssignment,
    Result,
    FeePayment
)


dashboard = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


@dashboard.route("/")
@login_required
def index():

    # =====================================================
    # TOTAL COUNTS
    # =====================================================

    total_students = Student.query.count()

    total_teachers = Teacher.query.count()

    total_classrooms = Classroom.query.count()

    total_subjects = Subject.query.count()

    total_sessions = SchoolSession.query.count()

    total_terms = Term.query.count()

    total_assignments = TeacherAssignment.query.count()

    total_results = Result.query.count()

    total_fee_payments = FeePayment.query.count()


    return render_template(
        "dashboard/index.html",

        user=current_user,

        total_students=total_students,

        total_teachers=total_teachers,

        total_classrooms=total_classrooms,

        total_subjects=total_subjects,

        total_sessions=total_sessions,

        total_terms=total_terms,

        total_assignments=total_assignments,

        total_results=total_results,

        total_fee_payments=total_fee_payments
    )