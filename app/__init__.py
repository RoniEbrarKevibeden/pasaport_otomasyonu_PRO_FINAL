import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
   
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this")

   
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    instance_dir = os.path.join(project_root, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, "app.db").replace("\\", "/")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    
    env_db = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    if env_db:
        app.config["SQLALCHEMY_DATABASE_URI"] = env_db

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REMEMBER_COOKIE_DURATION"] = 60 * 60 * 24 * 30  # 30 days

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "main.login"

    Limiter(get_remote_address, app=app, default_limits=["200/day", "50/hour"])

    
    app.serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    
    from .models import User, Application, AuditLog, Role

    with app.app_context():
        db.create_all()

        from werkzeug.security import generate_password_hash

        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_email and admin_password:
            
            if not User.query.filter_by(email=admin_email.strip().lower()).first():
                db.session.add(
                    User(
                        email=admin_email.strip().lower(),
                        password_hash=generate_password_hash(admin_password),
                        role=Role.ADMIN,
                        active=True,
                    )
                )
                db.session.commit()
        elif User.query.count() == 0:
            
            demo_users = [
                ("admin@example.com",   "Admin123!",   Role.ADMIN),
                ("officer@example.com", "Officer123!", Role.OFFICER),
                ("citizen@example.com", "Citizen123!", Role.CITIZEN),
            ]
            for email, pwd, role in demo_users:
                db.session.add(
                    User(
                        email=email,
                        password_hash=generate_password_hash(pwd),
                        role=role,
                        active=True,
                    )
                )
            db.session.commit()
        # -------------------------------------------------------------

    from .routes import bp as main_bp
    from .admin import bp_admin
    app.register_blueprint(main_bp)
    app.register_blueprint(bp_admin, url_prefix="/admin")

    return app
