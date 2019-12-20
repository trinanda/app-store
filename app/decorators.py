from functools import wraps

from flask import abort
from flask_login import current_user

from app.models import Permission


def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def operator_required(f):
    return permission_required(Permission.OPERATOR)(f)


def teacher_required(f):
    return permission_required(Permission.TEACHER)(f)


def student_required(f):
    return permission_required(Permission.STUDENT)(f)
