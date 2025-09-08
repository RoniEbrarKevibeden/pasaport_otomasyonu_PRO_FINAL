
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Simple RBAC permission map
PERMISSIONS = {
    "admin": {"manage_users", "view_audit", "review_applications", "submit_application"},
    "officer": {"review_applications"},
    "citizen": {"submit_application"},
}

def has_permission(user, perm: str) -> bool:
    if not user or not getattr(user, "role", None):
        return False
    return perm in PERMISSIONS.get(user.role, set())

def permission_required(*perms):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if not any(has_permission(current_user, p) for p in perms):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
