from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db
from models import Classroom


classroom = Blueprint(
    "classroom",
    __name__,
    url_prefix="/classrooms"
)


def admin_required():

    return current_user.is_authenticated and current_user.role == "admin"


@classroom.route("/")
@login_required
def list_classrooms():

    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()

    return render_template(
        "classroom/list.html",
        classrooms=classrooms
    )


@classroom.route("/create", methods=["GET", "POST"])
@login_required
def create_classroom():

    if not admin_required():

        flash(
            "Only administrators can create classes.",
            "danger"
        )

        return redirect(
            url_for("classroom.list_classrooms")
        )

    if request.method == "POST":

        name = request.form.get("name")

        if not name:

            flash(
                "Class name is required.",
                "danger"
            )

            return redirect(
                url_for("classroom.create_classroom")
            )

        existing = Classroom.query.filter_by(
            name=name
        ).first()

        if existing:

            flash(
                "This class already exists.",
                "danger"
            )

            return redirect(
                url_for("classroom.create_classroom")
            )

        new_class = Classroom(
            name=name
        )

        db.session.add(new_class)
        db.session.commit()

        flash(
            "Class created successfully.",
            "success"
        )

        return redirect(
            url_for("classroom.list_classrooms")
        )

    return render_template(
        "classroom/create.html"
    )


@classroom.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_classroom(id):

    if not admin_required():

        flash(
            "Only administrators can edit classes.",
            "danger"
        )

        return redirect(
            url_for("classroom.list_classrooms")
        )

    classroom_obj = db.get_or_404(
        Classroom,
        id
    )

    if request.method == "POST":

        name = request.form.get("name")

        if not name:

            flash(
                "Class name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "classroom.edit_classroom",
                    id=id
                )
            )

        classroom_obj.name = name

        db.session.commit()

        flash(
            "Class updated successfully.",
            "success"
        )

        return redirect(
            url_for("classroom.list_classrooms")
        )

    return render_template(
        "classroom/edit.html",
        classroom=classroom_obj
    )


@classroom.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_classroom(id):

    if not admin_required():

        flash(
            "Only administrators can delete classes.",
            "danger"
        )

        return redirect(
            url_for("classroom.list_classrooms")
        )

    classroom_obj = db.get_or_404(
        Classroom,
        id
    )

    db.session.delete(classroom_obj)

    db.session.commit()

    flash(
        "Class deleted successfully.",
        "success"
    )

    return redirect(
        url_for("classroom.list_classrooms")
    )