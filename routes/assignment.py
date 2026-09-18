from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models import (
    Teacher,
    Classroom,
    Subject,
    TeacherAssignment
)


assignment = Blueprint(
    "assignment",
    __name__,
    url_prefix="/assignments"
)


@assignment.route("/")
@login_required
def list_assignments():

    if current_user.role == "admin":

        assignments = TeacherAssignment.query.all()

    elif current_user.role == "teacher":

        assignments = TeacherAssignment.query.filter_by(
            teacher_id=current_user.teacher.id
        ).all()

    else:

        assignments = []

    return render_template(
        "assignment/list.html",
        assignments=assignments
    )


@assignment.route("/create", methods=["GET", "POST"])
@login_required
def create_assignment():

    if current_user.role != "admin":

        flash(
            "You do not have permission to assign teachers.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    teachers = Teacher.query.filter_by(
        is_active=True
    ).all()

    classrooms = Classroom.query.all()

    subjects = Subject.query.all()

    if request.method == "POST":

        teacher_id = request.form.get("teacher_id")
        classroom_id = request.form.get("classroom_id")
        subject_id = request.form.get("subject_id")

        existing = TeacherAssignment.query.filter_by(
            teacher_id=teacher_id,
            classroom_id=classroom_id,
            subject_id=subject_id
        ).first()

        if existing:

            flash(
                "This teacher is already assigned to this class and subject.",
                "warning"
            )

            return redirect(
                url_for("assignment.create_assignment")
            )

        new_assignment = TeacherAssignment(
            teacher_id=teacher_id,
            classroom_id=classroom_id,
            subject_id=subject_id
        )

        db.session.add(new_assignment)
        db.session.commit()

        flash(
            "Teacher assigned successfully.",
            "success"
        )

        return redirect(
            url_for("assignment.list_assignments")
        )

    return render_template(
        "assignment/create.html",
        teachers=teachers,
        classrooms=classrooms,
        subjects=subjects
    )


@assignment.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_assignment(id):

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    teacher_assignment = TeacherAssignment.query.get_or_404(id)

    db.session.delete(teacher_assignment)

    db.session.commit()

    flash(
        "Teacher assignment deleted.",
        "success"
    )

    return redirect(
        url_for("assignment.list_assignments")
    )