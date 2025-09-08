
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
    # absolute instance path + sqlite absolute uri
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    instance_dir = os.path.join(project_root, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, "app.db").replace("\\","/")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REMEMBER_COOKIE_DURATION"] = 60*60*24*30

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "main.login"

    Limiter(get_remote_address, app=app, default_limits=["200/day","50/hour"])
    app.serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    from .models import User, Application, AuditLog
    with app.app_context():
        db.create_all()

    from .routes import bp as main_bp
    from .admin import bp_admin
    app.register_blueprint(main_bp)
    app.register_blueprint(bp_admin, url_prefix="/admin")
    return app


    # --- Email (SMTP) configuration via environment variables ---
    # MAIL_ENABLED=true|false
    # MAIL_SERVER=smtp.example.com
    # MAIL_PORT=587
    # MAIL_USERNAME=your_username
    # MAIL_PASSWORD=your_password_or_app_password
    # MAIL_USE_TLS=true
    # MAIL_USE_SSL=false
    # MAIL_FROM=no-reply@example.com
