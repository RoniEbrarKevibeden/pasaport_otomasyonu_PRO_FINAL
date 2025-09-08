
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, current_app
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import BadSignature, SignatureExpired
from datetime import datetime
from . import db, login_manager
from .models import User, Application, AuditLog, Role, log_event
from .forms import LoginForm, ApplicationForm, ForgotPasswordForm, ResetPasswordForm
from .security import role_required
from .email_utils import send_mail
from werkzeug.security import check_password_hash, generate_password_hash

# ---- Blueprint ÖNCE tanımlanmalı ----
bp = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Kök URL -> /login'e yönlendir
@bp.get("/")
def index():
    return redirect(url_for("main.login"))

# Sadece /login ("/" bağlama!)
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    # Demo giriş butonları için
    demo = request.form.get("demo")
    if demo in {"citizen", "officer", "admin"}:
        email = f"{demo}@example.com"
        u = User.query.filter_by(email=email).first()
        if u and u.active:
            login_user(u, remember=True)
            u.last_login_at = datetime.utcnow()
            db.session.add(u)
            log_event(u.email, "LOGIN_DEMO", target="USER")
            db.session.commit()
            return redirect(url_for("main.dashboard"))

    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if u and check_password_hash(u.password_hash, form.password.data) and u.active:
            login_user(u, remember=form.remember.data)
            u.last_login_at = datetime.utcnow()
            db.session.add(u)
            log_event(u.email, "LOGIN", target="USER")
            db.session.commit()
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    log_event(current_user.email, "LOGOUT", target="USER")
    db.session.commit()
    logout_user()
    flash("Logged out.")
    return redirect(url_for("main.login"))

@bp.get("/dashboard")
@login_required
def dashboard():
    if current_user.role == Role.ADMIN:
        return render_template("admin_dashboard.html")
    if current_user.role == Role.OFFICER:
        apps = Application.query.order_by(Application.created_at.desc()).all()
        return render_template("officer_dashboard.html", apps=apps)
    # citizen
    apps = Application.query.order_by(Application.created_at.desc()).all()
    return render_template("citizen_dashboard.html", apps=apps)

@bp.route("/apply", methods=["GET", "POST"])
@login_required
@role_required(Role.CITIZEN, Role.ADMIN)
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        a = Application(
            citizen_name=form.full_name.data,
            national_id=form.national_id.data,
            birth_date=form.birth_date.data,
            address=form.address.data,
            passport_type=form.passport_type.data,
            status="PENDING",
        )
        db.session.add(a)
        db.session.commit()
        log_event(current_user.email, "CREATE_APP", target="APPLICATION", meta={"id": a.id})
        return redirect(url_for("main.dashboard"))
    return render_template("application_form.html", form=form)

@bp.post("/review/<int:app_id>/<string:action>")
@login_required
@role_required(Role.OFFICER, Role.ADMIN)
def review(app_id, action):
    a = Application.query.get_or_404(app_id)
    if action == "approve":
        a.status = "APPROVED"
    elif action == "deny":
        a.status = "DENIED"
    else:
        a.status = "SECONDARY"
    db.session.add(a)
    db.session.commit()
    log_event(current_user.email, f"REVIEW_{action.upper()}", target="APPLICATION", meta={"id": a.id})
    return redirect(url_for("main.dashboard"))

# ----- Admin -----
@bp.get("/admin/users")
@login_required
@role_required(Role.ADMIN)
def admin_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin_users.html", users=users)

@bp.post("/admin/users/<int:user_id>/role")
@login_required
@role_required(Role.ADMIN)
def admin_change_role(user_id):
    role = (request.form.get("role") or "").strip().lower()
    allowed = {Role.CITIZEN, Role.OFFICER, Role.ADMIN}
    if role not in allowed:
        flash("Invalid role.", "danger")
        return redirect(url_for("main.admin_users"))

    target = User.query.get_or_404(user_id)
    if target.id == current_user.id:
        flash("You cannot change your own role.", "warning")
        return redirect(url_for("main.admin_users"))

    if target.role != role:
        old = target.role
        target.role = role
        db.session.commit()
        try:
            log_event(actor=current_user.email, action="change_role", target="USER",
                      meta={"user_id": target.id, "old_role": old, "new_role": role})
        except Exception:
            pass
        flash(f"Role updated: {target.email} → {role}", "success")
    else:
        flash("Role unchanged.", "info")
    return redirect(url_for("main.admin_users"))

@bp.get("/admin/audit")
@login_required
@role_required(Role.ADMIN)
def admin_audit():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(300).all()
    return render_template("admin_audit.html", logs=logs)

# ----- Password reset -----
@bp.get("/forgot")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ForgotPasswordForm()
    return render_template("forgot_password.html", form=form)

@bp.post("/forgot")
def forgot_password_post():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ForgotPasswordForm()
    if not form.validate_on_submit():
        return render_template("forgot_password.html", form=form), 400
    user = User.query.filter_by(email=form.email.data.strip().lower()).first()
    msg = "If that email exists, we have sent a reset link."
    if not user:
        flash(msg, "info")
        return redirect(url_for("main.login"))
    token = getattr(current_app, "serializer").dumps(user.email, salt="pwd-reset")
    reset_url = url_for("main.reset_password", token=token, _external=True)
    sent, err = send_mail(user.email, "Password reset",
                          f"Use this link to reset your password: {reset_url}\nThis link expires in 1 hour.")
    if sent:
        flash(msg, "info")
    else:
        flash(f"(Demo) Password reset link: {reset_url}", "info")
    try:
        log_event(actor=user.email, action="request_password_reset", target="USER", meta={"user_id": user.id})
    except Exception:
        pass
    return redirect(url_for("main.login"))

@bp.get("/reset/<token>")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    return render_template("reset_password.html", form=form, token=token)

@bp.post("/reset/<token>")
def reset_password_post(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if not form.validate_on_submit():
        return render_template("reset_password.html", form=form, token=token), 400
    try:
        email = getattr(current_app, "serializer").loads(token, salt="pwd-reset", max_age=3600)
    except (BadSignature, SignatureExpired):
        flash("Reset link is invalid or expired.", "danger")
        return redirect(url_for("main.forgot_password"))
    user = User.query.filter_by(email=email).first_or_404()
    user.password_hash = generate_password_hash(form.password.data)
    db.session.commit()
    try:
        log_event(actor=email, action="password_reset", target="USER", meta={"user_id": user.id})
    except Exception:
        pass
    flash("Your password has been updated. Please sign in.", "success")
    return redirect(url_for("main.login"))
