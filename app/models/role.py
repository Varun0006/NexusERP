from app.extensions import db
from datetime import datetime


role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles")

    def has_permission(self, permission_name):
        return any(p.name == permission_name for p in self.permissions)

    def __repr__(self):
        return f"<Role {self.name}>"
