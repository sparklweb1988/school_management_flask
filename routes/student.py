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

from models import (
    User,
    Student,
    Classroom,
    TeacherAssignment
)


student = Blueprint(
    "student",
    __name__,
    url_prefix="/students"
)


# =========================================================
# LIST STUDENTS
# =========================================================

@student.route("/")
@login_required
def list_students():

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    if current_user.role == "admin":

        students = Student.query.order_by(
            Student.name
        ).all()


    # -----------------------------------------------------
    # TEACHER
    # -----------------------------------------------------

    elif current_user.role == "teacher":

        teacher = current_user.teacher

        classroom_ids = [
            assignment.classroom_id
            for assignment in teacher.assignments
        ]

        students = (
            Student.query
            .filter(
                Student.classroom_id.in_(classroom_ids)
            )
            .order_by(
                Student.name
            )
            .all()
            if classroom_ids
            else []
        )


    # -----------------------------------------------------
    # STUDENT
    # -----------------------------------------------------

    elif current_user.role == "student":

        students = [
            current_user.student
        ]


    else:

        students = []


    return render_template(
        "student/list.html",
        students=students
    )


# =========================================================
# CREATE STUDENT
# =========================================================

@student.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create_student():

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "Only administrators can create students.",
            "danger"
        )

        return redirect(
            url_for("student.list_students")
        )


    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()


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

        parent_name = request.form.get(
            "parent_name"
        )

        age = request.form.get(
            "age"
        )

        phone = request.form.get(
            "phone"
        )

        classroom_id = request.form.get(
            "classroom_id"
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
                url_for("student.create_student")
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
                url_for("student.create_student")
            )


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User(
            username=username,
            role="student",
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
        # CREATE STUDENT
        # -------------------------------------------------

        new_student = Student(
            user_id=user.id,
            name=name,
            parent_name=parent_name,
            age=int(age) if age else None,
            phone=phone,
            classroom_id=(
                int(classroom_id)
                if classroom_id
                else None
            ),
            is_active=True
        )


        db.session.add(
            new_student
        )

        db.session.commit()


        flash(
            "Student created successfully.",
            "success"
        )


        return redirect(
            url_for("student.list_students")
        )


    return render_template(
        "student/create.html",
        classrooms=classrooms
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@student.route(
    "/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_student(id):

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "Only administrators can edit students.",
            "danger"
        )

        return redirect(
            url_for("student.list_students")
        )


    student_obj = db.get_or_404(
        Student,
        id
    )


    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        student_obj.name = request.form.get(
            "name"
        )

        student_obj.parent_name = request.form.get(
            "parent_name"
        )

        age = request.form.get(
            "age"
        )


        try:

            student_obj.age = (
                int(age)
                if age
                else None
            )

        except ValueError:

            flash(
                "Age must be a valid number.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.edit_student",
                    id=id
                )
            )


        student_obj.phone = request.form.get(
            "phone"
        )


        classroom_id = request.form.get(
            "classroom_id"
        )


        student_obj.classroom_id = (
            int(classroom_id)
            if classroom_id
            else None
        )


        db.session.commit()


        flash(
            "Student updated successfully.",
            "success"
        )


        return redirect(
            url_for("student.list_students")
        )


    return render_template(
        "student/edit.html",
        student=student_obj,
        classrooms=classrooms
    )


# =========================================================
# TOGGLE STUDENT STATUS
# =========================================================

@student.route(
    "/<int:id>/toggle-status",
    methods=["POST"]
)
@login_required
def toggle_student_status(id):

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "You do not have permission to change student status.",
            "danger"
        )

        return redirect(
            url_for("student.list_students")
        )


    # -----------------------------------------------------
    # GET STUDENT
    # -----------------------------------------------------

    student_obj = db.get_or_404(
        Student,
        id
    )


    # -----------------------------------------------------
    # TOGGLE
    # -----------------------------------------------------

    student_obj.is_active = not student_obj.is_active


    # Also control login

    student_obj.user.is_active = (
        student_obj.is_active
    )


    db.session.commit()


    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    if student_obj.is_active:

        flash(
            f"{student_obj.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{student_obj.name} has been deactivated.",
            "warning"
        )


    return redirect(
        url_for("student.list_students")
    )


# =========================================================
# STUDENT ASSIGNMENTS
# =========================================================

@student.route(
    "/assignments",
    methods=["GET", "POST"]
)
@login_required
def student_assignments():

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "You do not have permission.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )


    students = Student.query.order_by(
        Student.name
    ).all()


    classrooms = Classroom.query.order_by(
        Classroom.name
    ).all()


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        try:

            student_id = int(
                request.form.get(
                    "student_id"
                )
            )

            classroom_id = int(
                request.form.get(
                    "classroom_id"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            flash(
                "Please select a student and classroom.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.student_assignments"
                )
            )


        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        student_obj = Student.query.get(
            student_id
        )


        if not student_obj:

            flash(
                "Student not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.student_assignments"
                )
            )


        # -------------------------------------------------
        # GET CLASSROOM
        # -------------------------------------------------

        classroom = Classroom.query.get(
            classroom_id
        )


        if not classroom:

            flash(
                "Classroom not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.student_assignments"
                )
            )


        # -------------------------------------------------
        # ASSIGN
        # -------------------------------------------------

        student_obj.classroom_id = (
            classroom.id
        )


        db.session.commit()


        flash(
            f"{student_obj.name} has been assigned to {classroom.name}.",
            "success"
        )


        return redirect(
            url_for(
                "student.student_assignments"
            )
        )


    return render_template(
        "student/assignments.html",
        students=students,
        classrooms=classrooms
    )


# =========================================================
# MY CLASS
# =========================================================

@student.route(
    "/my-class"
)
@login_required
def my_class():

    # -----------------------------------------------------
    # ONLY STUDENT
    # -----------------------------------------------------

    if current_user.role != "student":

        flash(
            "This page is for students only.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )


    student_obj = current_user.student


    # -----------------------------------------------------
    # NO CLASS
    # -----------------------------------------------------

    if not student_obj.classroom:

        return render_template(
            "student/my_class.html",
            student=student_obj,
            classroom=None,
            assignments=[],
            teachers=[]
        )


    classroom = student_obj.classroom


    # -----------------------------------------------------
    # GET CLASS ASSIGNMENTS
    # -----------------------------------------------------

    assignments = TeacherAssignment.query.filter_by(
        classroom_id=classroom.id
    ).all()


    # -----------------------------------------------------
    # GET TEACHERS
    # -----------------------------------------------------

    teachers = []

    for assignment in assignments:

        if assignment.teacher not in teachers:

            teachers.append(
                assignment.teacher
            )


    return render_template(
        "student/my_class.html",
        student=student_obj,
        classroom=classroom,
        assignments=assignments,
        teachers=teachers
    )