from app.extensions import db
from app.models.permission import Permission


class PermissionService:
    @staticmethod
    def create_permission(name, codename, module, description=None):
        if Permission.query.filter_by(codename=codename).first():
            return None, "Permission already exists"
        permission = Permission(
            name=name, codename=codename, module=module, description=description
        )
        db.session.add(permission)
        db.session.commit()
        return permission, None

    @staticmethod
    def has_permission(user, permission_codename):
        if not user.role:
            return False
        return user.role.has_permission(permission_codename)

    @staticmethod
    def user_has_module_access(user, module_name):
        module_permissions = [
            f"view_{module_name}",
            f"create_{module_name}",
            f"edit_{module_name}",
            f"delete_{module_name}",
        ]
        return any(user.has_permission(p) for p in module_permissions) if user.role else False
