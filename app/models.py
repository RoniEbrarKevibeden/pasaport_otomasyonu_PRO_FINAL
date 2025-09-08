
from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from json import dumps

class Role:
    CITIZEN="citizen"; OFFICER="officer"; ADMIN="admin"

class User(db.Model, UserMixin):
    def has_role(self, *roles):
        return self.role in roles

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=Role.CITIZEN, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, raw): self.password_hash = generate_password_hash(raw)
    def check_password(self, raw): return check_password_hash(self.password_hash, raw)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    citizen_name = db.Column(db.String(120), nullable=False)
    national_id = db.Column(db.String(32), nullable=False)
    birth_date = db.Column(db.String(10), nullable=False) # yyyy-mm-dd
    address = db.Column(db.String(255), nullable=False)
    passport_type = db.Column(db.String(30), nullable=False) # Ordinary/Service/Special
    status = db.Column(db.String(20), default="PENDING", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String(180))
    action = db.Column(db.String(200))
    target = db.Column(db.String(80))    # USER/APPLICATION/SYSTEM
    meta = db.Column(db.Text)            # small json
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def log_event(actor, action, target=None, meta=None):
    entry = AuditLog(actor=actor, action=action, target=target, meta=dumps(meta) if isinstance(meta,(dict,list)) else meta)
    db.session.add(entry)
    db.session.commit()
