from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db

from models import (
    SchoolFee,
    Classroom,
    SchoolSession,
    Term
)


fee = Blueprint(
    "fee",
    __name__
)


# =========================================================
# SCHOOL FEE LIST
# =========================================================

@fee.route("/school-fees")
@login_required
def school_fees():

    if current_user.role != "admin":
        return "Access denied", 403

    fees = SchoolFee.query.order_by(
        SchoolFee.created_at.desc()
    ).all()

    return render_template(
        "schoolfee/list.html",
        fees=fees
    )


# =========================================================
# CREATE SCHOOL FEE
# =========================================================

@fee.route(
    "/school-fees/create",
    methods=["GET", "POST"]
)
@login_required
def school_fee_create():

    if current_user.role != "admin":
        return "Access denied", 403

    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()

    sessions = SchoolSession.query.order_by(
        SchoolSession.year.desc()
    ).all()

    terms = Term.query.order_by(
        Term.name
    ).all()

    if request.method == "POST":

        classroom_id = request.form["classroom_id"]

        session_id = request.form["session_id"]

        term_id = request.form["term_id"]

        amount = request.form["amount"]

        description = request.form["description"]


        school_fee = SchoolFee(

            classroom_id=classroom_id,

            session_id=session_id,

            term_id=term_id,

            amount=amount,

            description=description

        )


        db.session.add(school_fee)

        db.session.commit()


        return redirect(
            url_for("fee.school_fees")
        )


    return render_template(
        "schoolfee/create.html",

        classrooms=classrooms,

        sessions=sessions,

        terms=terms
    )


# =========================================================
# EDIT SCHOOL FEE
# =========================================================

@fee.route(
    "/school-fees/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def school_fee_edit(id):

    if current_user.role != "admin":
        return "Access denied", 403


    school_fee = SchoolFee.query.get_or_404(id)


    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()

    sessions = SchoolSession.query.order_by(
        SchoolSession.year.desc()
    ).all()

    terms = Term.query.order_by(
        Term.name
    ).all()


    if request.method == "POST":

        school_fee.classroom_id = request.form[
            "classroom_id"
        ]

        school_fee.session_id = request.form[
            "session_id"
        ]

        school_fee.term_id = request.form[
            "term_id"
        ]

        school_fee.amount = request.form[
            "amount"
        ]

        school_fee.description = request.form[
            "description"
        ]


        db.session.commit()


        return redirect(
            url_for("fee.school_fees")
        )


    return render_template(
        "schoolfee/edit.html",

        fee=school_fee,

        classrooms=classrooms,

        sessions=sessions,

        terms=terms
    )


# =========================================================
# DELETE SCHOOL FEE
# =========================================================

@fee.route(
    "/school-fees/<int:id>/delete"
)
@login_required
def school_fee_delete(id):

    if current_user.role != "admin":
        return "Access denied", 403


    school_fee = SchoolFee.query.get_or_404(id)


    db.session.delete(school_fee)

    db.session.commit()


    return redirect(
        url_for("fee.school_fees")
    )