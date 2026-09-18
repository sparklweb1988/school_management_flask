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
from models import Subject


subject = Blueprint(
    "subject",
    __name__,
    url_prefix="/subjects"
)


def admin_required():

    return current_user.is_authenticated and current_user.role == "admin"


@subject.route("/")
@login_required
def list_subjects():

    subjects = Subject.query.order_by(
        Subject.name
    ).all()

    return render_template(
        "subject/list.html",
        subjects=subjects
    )


@subject.route("/create", methods=["GET", "POST"])
@login_required
def create_subject():

    if not admin_required():

        flash(
            "Only administrators can create subjects.",
            "danger"
        )

        return redirect(
            url_for("subject.list_subjects")
        )

    if request.method == "POST":

        name = request.form.get("name")

        if not name:

            flash(
                "Subject name is required.",
                "danger"
            )

            return redirect(
                url_for("subject.create_subject")
            )

        existing = Subject.query.filter_by(
            name=name
        ).first()

        if existing:

            flash(
                "This subject already exists.",
                "danger"
            )

            return redirect(
                url_for("subject.create_subject")
            )

        new_subject = Subject(
            name=name
        )

        db.session.add(new_subject)

        db.session.commit()

        flash(
            "Subject created successfully.",
            "success"
        )

        return redirect(
            url_for("subject.list_subjects")
        )

    return render_template(
        "subject/create.html"
    )


@subject.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(id):

    if not admin_required():

        flash(
            "Only administrators can edit subjects.",
            "danger"
        )

        return redirect(
            url_for("subject.list_subjects")
        )

    subject_obj = db.get_or_404(
        Subject,
        id
    )

    if request.method == "POST":

        name = request.form.get("name")

        if not name:

            flash(
                "Subject name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "subject.edit_subject",
                    id=id
                )
            )

        subject_obj.name = name

        db.session.commit()

        flash(
            "Subject updated successfully.",
            "success"
        )

        return redirect(
            url_for("subject.list_subjects")
        )

    return render_template(
        "subject/edit.html",
        subject=subject_obj
    )


@subject.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_subject(id):

    if not admin_required():

        flash(
            "Only administrators can delete subjects.",
            "danger"
        )

        return redirect(
            url_for("subject.list_subjects")
        )

    subject_obj = db.get_or_404(
        Subject,
        id
    )

    db.session.delete(subject_obj)

    db.session.commit()

    flash(
        "Subject deleted successfully.",
        "success"
    )

    return redirect(
        url_for("subject.list_subjects")
    )