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
from models import SchoolSession


session = Blueprint(
    "session",
    __name__,
    url_prefix="/sessions"
)


@session.route("/")
@login_required
def list_sessions():

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    sessions = SchoolSession.query.order_by(
        SchoolSession.year.desc()
    ).all()

    return render_template(
        "session/list.html",
        sessions=sessions
    )


@session.route("/create", methods=["GET", "POST"])
@login_required
def create_session():

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":

        year = request.form.get("year")

        existing = SchoolSession.query.filter_by(
            year=year
        ).first()

        if existing:

            flash(
                "This session already exists.",
                "warning"
            )

            return redirect(
                url_for("session.create_session")
            )

        new_session = SchoolSession(
            year=year
        )

        db.session.add(new_session)

        db.session.commit()

        flash(
            "Session created successfully.",
            "success"
        )

        return redirect(
            url_for("session.list_sessions")
        )

    return render_template(
        "session/create.html"
    )