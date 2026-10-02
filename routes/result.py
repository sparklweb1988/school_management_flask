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
    Result,
    Student,
    Subject,
    Classroom,
    SchoolSession,
    Term,
    TeacherAssignment
)


result = Blueprint(
    "result",
    __name__,
    url_prefix="/results"
)


# =========================================================
# LIST RESULTS
# =========================================================

@result.route("/")
@login_required
def list_results():

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    if current_user.role == "admin":

        results = (
            Result.query
            .order_by(Result.id.desc())
            .all()
        )


    # -----------------------------------------------------
    # TEACHER
    # -----------------------------------------------------

    elif current_user.role == "teacher":

        teacher = current_user.teacher

        assignments = (
            TeacherAssignment.query
            .filter_by(teacher_id=teacher.id)
            .all()
        )

        allowed_pairs = {
            (
                assignment.classroom_id,
                assignment.subject_id
            )
            for assignment in assignments
        }

        all_results = (
            Result.query
            .order_by(Result.id.desc())
            .all()
        )

        results = [
            item
            for item in all_results
            if (
                item.classroom_id,
                item.subject_id
            ) in allowed_pairs
        ]


    # -----------------------------------------------------
    # STUDENT
    # -----------------------------------------------------

    elif current_user.role == "student":

        results = (
            Result.query
            .filter_by(
                student_id=current_user.student.id
            )
            .order_by(Result.id.desc())
            .all()
        )


    else:

        results = []


    return render_template(
        "result/list.html",
        results=results
    )


# =========================================================
# CREATE RESULT
# =========================================================

@result.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create_result():

    # -----------------------------------------------------
    # ONLY ADMIN AND TEACHER
    # -----------------------------------------------------

    if current_user.role not in [
        "admin",
        "teacher"
    ]:

        flash(
            "You are not allowed to enter results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    # =====================================================
    # ADMIN DATA
    # =====================================================

    if current_user.role == "admin":

        students = (
            Student.query
            .order_by(Student.name)
            .all()
        )

        subjects = (
            Subject.query
            .order_by(Subject.name)
            .all()
        )

        classrooms = (
            Classroom.query
            .order_by(Classroom.name)
            .all()
        )


    # =====================================================
    # TEACHER DATA
    # =====================================================

    else:

        teacher = current_user.teacher

        assignments = (
            TeacherAssignment.query
            .filter_by(teacher_id=teacher.id)
            .all()
        )

        classroom_ids = list({
            assignment.classroom_id
            for assignment in assignments
        })

        subject_ids = list({
            assignment.subject_id
            for assignment in assignments
        })


        students = (
            Student.query
            .filter(
                Student.classroom_id.in_(classroom_ids),
                Student.is_active == True
            )
            .order_by(Student.name)
            .all()
            if classroom_ids
            else []
        )


        subjects = (
            Subject.query
            .filter(
                Subject.id.in_(subject_ids)
            )
            .order_by(Subject.name)
            .all()
            if subject_ids
            else []
        )


        classrooms = (
            Classroom.query
            .filter(
                Classroom.id.in_(classroom_ids)
            )
            .order_by(Classroom.name)
            .all()
            if classroom_ids
            else []
        )


    # =====================================================
    # SESSIONS
    # =====================================================

    sessions = (
        SchoolSession.query
        .order_by(SchoolSession.year)
        .all()
    )


    # =====================================================
    # TERMS
    # =====================================================

    terms = (
        Term.query
        .order_by(Term.name)
        .all()
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        try:

            student_id = int(
                request.form.get("student_id")
            )

            subject_id = int(
                request.form.get("subject_id")
            )

            classroom_id = int(
                request.form.get("classroom_id")
            )

            session_id = int(
                request.form.get("session_id")
            )

            term_id = int(
                request.form.get("term_id")
            )

            ca_score = float(
                request.form.get("ca_score") or 0
            )

            exam_score = float(
                request.form.get("exam_score") or 0
            )

        except (
            TypeError,
            ValueError
        ):

            flash(
                "Please enter valid result information.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # SCORE VALIDATION
        # -------------------------------------------------

        if ca_score < 0 or ca_score > 40:

            flash(
                "CA score must be between 0 and 40.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        if exam_score < 0 or exam_score > 60:

            flash(
                "Exam score must be between 0 and 60.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        student = Student.query.get(student_id)

        if not student:

            flash(
                "Student not found.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # GET SUBJECT
        # -------------------------------------------------

        subject = Subject.query.get(subject_id)

        if not subject:

            flash(
                "Subject not found.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # GET CLASSROOM
        # -------------------------------------------------

        classroom = Classroom.query.get(classroom_id)

        if not classroom:

            flash(
                "Classroom not found.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # STUDENT MUST BELONG TO CLASSROOM
        # -------------------------------------------------

        if student.classroom_id != classroom.id:

            flash(
                "This student does not belong to the selected classroom.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # TEACHER PERMISSION
        # -------------------------------------------------

        if current_user.role == "teacher":

            allowed = (
                TeacherAssignment.query
                .filter_by(
                    teacher_id=current_user.teacher.id,
                    classroom_id=classroom_id,
                    subject_id=subject_id
                )
                .first()
            )

            if not allowed:

                flash(
                    "You are not assigned to this class and subject.",
                    "danger"
                )

                return redirect(
                    url_for("result.create_result")
                )


        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        existing = (
            Result.query
            .filter_by(
                student_id=student_id,
                subject_id=subject_id,
                session_id=session_id,
                term_id=term_id
            )
            .first()
        )


        if existing:

            flash(
                "A result already exists for this student, subject, session and term.",
                "danger"
            )

            return redirect(
                url_for("result.create_result")
            )


        # -------------------------------------------------
        # CREATE RESULT
        # -------------------------------------------------

        new_result = Result(
            student_id=student_id,
            subject_id=subject_id,
            classroom_id=classroom_id,
            session_id=session_id,
            term_id=term_id,
            ca_score=ca_score,
            exam_score=exam_score
        )


        db.session.add(new_result)

        db.session.commit()


        flash(
            "Result created successfully.",
            "success"
        )


        return redirect(
            url_for("result.list_results")
        )


    return render_template(
        "result/create.html",
        students=students,
        subjects=subjects,
        classrooms=classrooms,
        sessions=sessions,
        terms=terms
    )


# =========================================================
# EDIT RESULT
# =========================================================

@result.route(
    "/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_result(id):

    result_obj = db.get_or_404(
        Result,
        id
    )


    # -----------------------------------------------------
    # STUDENT CANNOT EDIT
    # -----------------------------------------------------

    if current_user.role == "student":

        flash(
            "You cannot edit results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    # -----------------------------------------------------
    # TEACHER PERMISSION
    # -----------------------------------------------------

    if current_user.role == "teacher":

        allowed = (
            TeacherAssignment.query
            .filter_by(
                teacher_id=current_user.teacher.id,
                classroom_id=result_obj.classroom_id,
                subject_id=result_obj.subject_id
            )
            .first()
        )


        if not allowed:

            flash(
                "You are not allowed to edit this result.",
                "danger"
            )

            return redirect(
                url_for("result.list_results")
            )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        try:

            ca_score = float(
                request.form.get("ca_score") or 0
            )

            exam_score = float(
                request.form.get("exam_score") or 0
            )

        except (
            TypeError,
            ValueError
        ):

            flash(
                "Please enter valid scores.",
                "danger"
            )

            return redirect(
                url_for(
                    "result.edit_result",
                    id=id
                )
            )


        if ca_score < 0 or ca_score > 40:

            flash(
                "CA score must be between 0 and 40.",
                "danger"
            )

            return redirect(
                url_for(
                    "result.edit_result",
                    id=id
                )
            )


        if exam_score < 0 or exam_score > 60:

            flash(
                "Exam score must be between 0 and 60.",
                "danger"
            )

            return redirect(
                url_for(
                    "result.edit_result",
                    id=id
                )
            )


        result_obj.ca_score = ca_score

        result_obj.exam_score = exam_score


        db.session.commit()


        flash(
            "Result updated successfully.",
            "success"
        )


        return redirect(
            url_for("result.list_results")
        )


    return render_template(
        "result/edit.html",
        result=result_obj
    )


# =========================================================
# PRINT SINGLE RESULT
# =========================================================

@result.route(
    "/<int:id>/print"
)
@login_required
def print_result(id):

    # -----------------------------------------------------
    # STUDENTS CANNOT PRINT
    # -----------------------------------------------------

    if current_user.role == "student":

        flash(
            "You are not allowed to print results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    result_obj = db.get_or_404(
        Result,
        id
    )


    # -----------------------------------------------------
    # TEACHER PERMISSION
    # -----------------------------------------------------

    if current_user.role == "teacher":

        allowed = (
            TeacherAssignment.query
            .filter_by(
                teacher_id=current_user.teacher.id,
                classroom_id=result_obj.classroom_id,
                subject_id=result_obj.subject_id
            )
            .first()
        )


        if not allowed:

            flash(
                "You are not allowed to print this result.",
                "danger"
            )

            return redirect(
                url_for("result.list_results")
            )


    return render_template(
        "result/print.html",
        result=result_obj
    )


# =========================================================
# SELECT SUBJECTS TO PRINT FOR A STUDENT
# =========================================================

@result.route(
    "/student/print",
    methods=["GET"]
)
@login_required
def print_student_result():

    # -----------------------------------------------------
    # STUDENTS CANNOT USE THIS PAGE
    # -----------------------------------------------------

    if current_user.role == "student":

        flash(
            "You are not allowed to print results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    if current_user.role == "admin":

        students = (
            Student.query
            .filter_by(is_active=True)
            .order_by(Student.name)
            .all()
        )

    else:

        teacher = current_user.teacher

        assignments = (
            TeacherAssignment.query
            .filter_by(teacher_id=teacher.id)
            .all()
        )

        classroom_ids = list({
            assignment.classroom_id
            for assignment in assignments
        })


        students = (
            Student.query
            .filter(
                Student.classroom_id.in_(classroom_ids),
                Student.is_active == True
            )
            .order_by(Student.name)
            .all()
            if classroom_ids
            else []
        )


    # -----------------------------------------------------
    # SESSIONS
    # -----------------------------------------------------

    sessions = (
        SchoolSession.query
        .order_by(SchoolSession.year.desc())
        .all()
    )


    # -----------------------------------------------------
    # TERMS
    # -----------------------------------------------------

    terms = (
        Term.query
        .order_by(Term.name)
        .all()
    )


    # -----------------------------------------------------
    # SELECTED FILTERS
    # -----------------------------------------------------

    student_id = request.args.get(
        "student_id",
        type=int
    )

    session_id = request.args.get(
        "session_id",
        type=int
    )

    term_id = request.args.get(
        "term_id",
        type=int
    )


    results = []


    # -----------------------------------------------------
    # LOAD STUDENT RESULTS
    # -----------------------------------------------------

    if student_id and session_id and term_id:

        student = Student.query.get(
            student_id
        )


        if not student:

            flash(
                "Student not found.",
                "danger"
            )

            return redirect(
                url_for("result.print_student_result")
            )


        query = (
            Result.query
            .filter_by(
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
            .order_by(Result.subject_id)
        )


        all_student_results = query.all()


        # -------------------------------------------------
        # TEACHER PERMISSION
        # -------------------------------------------------

        if current_user.role == "teacher":

            teacher = current_user.teacher

            assignments = (
                TeacherAssignment.query
                .filter_by(teacher_id=teacher.id)
                .all()
            )


            allowed_pairs = {
                (
                    assignment.classroom_id,
                    assignment.subject_id
                )
                for assignment in assignments
            }


            results = [
                item
                for item in all_student_results
                if (
                    item.classroom_id,
                    item.subject_id
                ) in allowed_pairs
            ]

        else:

            results = all_student_results


    return render_template(
        "result/select_print.html",
        students=students,
        sessions=sessions,
        terms=terms,
        results=results,
        selected_student_id=student_id,
        selected_session_id=session_id,
        selected_term_id=term_id
    )


# =========================================================
# PRINT SELECTED SUBJECTS
# =========================================================

@result.route(
    "/student/print/selected",
    methods=["POST"]
)
@login_required
def print_selected_student_result():

    # -----------------------------------------------------
    # STUDENTS CANNOT PRINT
    # -----------------------------------------------------

    if current_user.role == "student":

        flash(
            "You are not allowed to print results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    # -----------------------------------------------------
    # GET FILTER VALUES
    # -----------------------------------------------------

    try:

        student_id = int(
            request.form.get("student_id")
        )

        session_id = int(
            request.form.get("session_id")
        )

        term_id = int(
            request.form.get("term_id")
        )

    except (
        TypeError,
        ValueError
    ):

        flash(
            "Please select a student, session and term.",
            "danger"
        )

        return redirect(
            url_for("result.print_student_result")
        )


    # -----------------------------------------------------
    # GET SELECTED SUBJECTS
    # -----------------------------------------------------

    subject_ids = request.form.getlist(
        "subject_ids"
    )


    if not subject_ids:

        flash(
            "Please select at least one subject to print.",
            "warning"
        )

        return redirect(
            url_for(
                "result.print_student_result",
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
        )


    # -----------------------------------------------------
    # CONVERT SUBJECT IDS TO INTEGER
    # -----------------------------------------------------

    try:

        subject_ids = [
            int(subject_id)
            for subject_id in subject_ids
        ]

    except (
        TypeError,
        ValueError
    ):

        flash(
            "Invalid subject selection.",
            "danger"
        )

        return redirect(
            url_for(
                "result.print_student_result",
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
        )


    # -----------------------------------------------------
    # GET STUDENT
    # -----------------------------------------------------

    student = Student.query.get(
        student_id
    )


    if not student:

        flash(
            "Student not found.",
            "danger"
        )

        return redirect(
            url_for("result.print_student_result")
        )


    # -----------------------------------------------------
    # TEACHER: VERIFY STUDENT IS ALLOWED
    # -----------------------------------------------------

    if current_user.role == "teacher":

        teacher = current_user.teacher

        student_classroom_id = student.classroom_id


        teacher_has_student_access = (
            TeacherAssignment.query
            .filter_by(
                teacher_id=teacher.id,
                classroom_id=student_classroom_id
            )
            .first()
        )


        if not teacher_has_student_access:

            flash(
                "You are not allowed to print results for this student.",
                "danger"
            )

            return redirect(
                url_for("result.print_student_result")
            )


    # -----------------------------------------------------
    # GET SELECTED RESULTS
    # -----------------------------------------------------

    results = (
        Result.query
        .filter(
            Result.student_id == student_id,
            Result.session_id == session_id,
            Result.term_id == term_id,
            Result.subject_id.in_(subject_ids)
        )
        .order_by(Result.subject_id)
        .all()
    )


    # -----------------------------------------------------
    # TEACHER PERMISSION FOR SUBJECTS
    # -----------------------------------------------------

    if current_user.role == "teacher":

        teacher = current_user.teacher

        assignments = (
            TeacherAssignment.query
            .filter_by(teacher_id=teacher.id)
            .all()
        )


        allowed_pairs = {
            (
                assignment.classroom_id,
                assignment.subject_id
            )
            for assignment in assignments
        }


        results = [
            item
            for item in results
            if (
                item.classroom_id,
                item.subject_id
            ) in allowed_pairs
        ]


    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not results:

        flash(
            "No valid results were found for the selected subjects.",
            "warning"
        )

        return redirect(
            url_for(
                "result.print_student_result",
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
        )


    # -----------------------------------------------------
    # PRINT PAGE
    # -----------------------------------------------------

    return render_template(
        "result/print_selected.html",
        student=student,
        results=results,
        session=results[0].session,
        term=results[0].term
    )


# =========================================================
# DELETE RESULT
# =========================================================

@result.route(
    "/<int:id>/delete",
    methods=["POST"]
)
@login_required
def delete_result(id):

    # -----------------------------------------------------
    # ONLY ADMIN
    # -----------------------------------------------------

    if current_user.role != "admin":

        flash(
            "Only administrators can delete results.",
            "danger"
        )

        return redirect(
            url_for("result.list_results")
        )


    result_obj = db.get_or_404(
        Result,
        id
    )


    db.session.delete(
        result_obj
    )

    db.session.commit()


    flash(
        "Result deleted successfully.",
        "success"
    )


    return redirect(
        url_for("result.list_results")
    )
