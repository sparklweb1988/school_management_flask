from app import app
from extensions import db
from models import User


with app.app_context():

    username = input("Admin username: ")
    password = input("Admin password: ")

    existing = User.query.filter_by(
        username=username
    ).first()

    if existing:

        print("User already exists.")

    else:

        admin = User(
            username=username,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)

        db.session.commit()

        print("Admin created successfully.")