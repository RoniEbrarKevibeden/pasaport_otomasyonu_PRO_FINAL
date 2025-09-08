
from app import create_app, db
from app.models import User, Application, Role
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.drop_all(); db.create_all()
    pwd = generate_password_hash("Password!23")
    users = [
        User(email="citizen@example.com", password_hash=pwd, role=Role.CITIZEN),
        User(email="officer@example.com", password_hash=pwd, role=Role.OFFICER),
        User(email="admin@example.com", password_hash=pwd, role=Role.ADMIN),
    ]
    db.session.add_all(users); db.session.commit()
    print("Seeded demo users: citizen/officer/admin@example.com | Password: Password!23")
