from app.extensions import db
from app.models.user import User
from app.models.audit_log import AuditLog


class AuthService:
    @staticmethod
    def register(username, email, password, full_name=None, role_id=None):
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role_id=role_id,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials"
        if not user.is_active:
            return None, "Account is deactivated"
        return user, None

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            return False, "Current password is incorrect"
        user.set_password(new_password)
        db.session.commit()
        return True, "Password changed successfully"
