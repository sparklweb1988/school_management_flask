from flask import Flask, render_template
import webview
from config import Config
from extensions import db, login_manager

from models import User


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"


    with app.app_context():

            db.create_all()


    # -------------------------
    # USER LOADER
    # -------------------------

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )


    # -------------------------
    # BLUEPRINTS
    # -------------------------

    from routes.auth import auth
    from routes.dashboard import dashboard
    from routes.classroom import classroom
    from routes.subject import subject
    from routes.teacher import teacher
    from routes.student import student
    from routes.assignment import assignment
    from routes.result import result
    from routes.session import session
    from routes.term import term
    from routes.fee import fee
    from routes.payment import payment


    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(classroom)
    app.register_blueprint(subject)
    app.register_blueprint(teacher)
    app.register_blueprint(student)
    app.register_blueprint(assignment)
    app.register_blueprint(result)
    app.register_blueprint(session)
    app.register_blueprint(term)
    app.register_blueprint(fee)
    app.register_blueprint(payment)


    # -------------------------
    # HOME
    # -------------------------

    @app.route("/")
    def home():

        return render_template(
            "home.html"
        )


    # -------------------------
    # RETURN APP
    # -------------------------

    return app


app = create_app()


if __name__ == "__main__":

    # webview.create_window(
    #      'School Management System', app
    # )

   
    app.run(debug=True)
    # webview.start()