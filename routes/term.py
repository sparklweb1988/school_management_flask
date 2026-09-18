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
from models import Term


term = Blueprint(
    "term",
    __name__,
    url_prefix="/terms"
)


@term.route("/")
@login_required
def list_terms():

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    terms = Term.query.order_by(
        Term.name
    ).all()

    return render_template(
        "term/list.html",
        terms=terms
    )


@term.route("/create", methods=["GET", "POST"])
@login_required
def create_term():

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":

        name = request.form.get("name")

        existing = Term.query.filter_by(
            name=name
        ).first()

        if existing:

            flash(
                "This term already exists.",
                "warning"
            )

            return redirect(
                url_for("term.create_term")
            )

        new_term = Term(
            name=name
        )

        db.session.add(new_term)

        db.session.commit()

        flash(
            "Term created successfully.",
            "success"
        )

        return redirect(
            url_for("term.list_terms")
        )

    return render_template(
        "term/create.html"
    )