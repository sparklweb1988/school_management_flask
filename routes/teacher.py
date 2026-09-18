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
from models import User, Teacher


teacher = Blueprint(
    "teacher",
    __name__,
    url_prefix="/teachers"
)


# =========================================================
# LIST TEACHERS
# =========================================================

@teacher.route("/")
@login_required
def list_teachers():

    teachers = Teacher.query.order_by(
        Teacher.name
    ).all()

    return render_template(
        "teacher/list.html",
        teachers=teachers
    )


# =========================================================
# CREATE TEACHER
# =========================================================

@teacher.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create_teacher():

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "Only administrators can create teachers.",
            "danger"
        )

        return redirect(
            url_for("teacher.list_teachers")
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        name = request.form.get(
            "name"
        )

        phone = request.form.get(
            "phone"
        )


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not password or not name:

            flash(
                "Username, password and name are required.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_teacher")
            )


        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            username=username
        ).first()


        if existing_user:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_teacher")
            )


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User(
            username=username,
            role="teacher",
            is_active=True
        )

        user.set_password(
            password
        )


        db.session.add(
            user
        )

        db.session.flush()


        # -------------------------------------------------
        # CREATE TEACHER
        # -------------------------------------------------

        new_teacher = Teacher(
            user_id=user.id,
            name=name,
            phone=phone,
            is_active=True
        )


        db.session.add(
            new_teacher
        )

        db.session.commit()


        flash(
            "Teacher created successfully.",
            "success"
        )


        return redirect(
            url_for("teacher.list_teachers")
        )


    return render_template(
        "teacher/create.html"
    )


# =========================================================
# EDIT TEACHER
# =========================================================

@teacher.route(
    "/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_teacher(id):

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "Only administrators can edit teachers.",
            "danger"
        )

        return redirect(
            url_for("teacher.list_teachers")
        )


    teacher_obj = db.get_or_404(
        Teacher,
        id
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        teacher_obj.name = request.form.get(
            "name"
        )

        teacher_obj.phone = request.form.get(
            "phone"
        )


        db.session.commit()


        flash(
            "Teacher updated successfully.",
            "success"
        )


        return redirect(
            url_for("teacher.list_teachers")
        )


    return render_template(
        "teacher/edit.html",
        teacher=teacher_obj
    )


# =========================================================
# ACTIVATE / DEACTIVATE TEACHER
# =========================================================

@teacher.route(
    "/<int:id>/toggle-status",
    methods=["POST"]
)
@login_required
def toggle_teacher_status(id):

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "You do not have permission to change teacher status.",
            "danger"
        )

        return redirect(
            url_for("teacher.list_teachers")
        )


    # -----------------------------------------------------
    # GET TEACHER
    # -----------------------------------------------------

    teacher_obj = db.get_or_404(
        Teacher,
        id
    )


    # -----------------------------------------------------
    # TOGGLE TEACHER STATUS
    # -----------------------------------------------------

    teacher_obj.is_active = not teacher_obj.is_active


    # -----------------------------------------------------
    # ALSO TOGGLE USER LOGIN
    # -----------------------------------------------------

    teacher_obj.user.is_active = (
        teacher_obj.is_active
    )


    db.session.commit()


    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    if teacher_obj.is_active:

        flash(
            f"{teacher_obj.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{teacher_obj.name} has been deactivated.",
            "warning"
        )


    return redirect(
        url_for("teacher.list_teachers")
    )