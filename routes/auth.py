from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from models import User


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if not user or not user.check_password(password):

            flash(
                "Invalid username or password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_active:

            flash(
                "Your account is inactive.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        login_user(user)

        return redirect(
            url_for("dashboard.index")
        )

    return render_template(
        "auth/login.html"
    )


@auth.route("/logout")
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )