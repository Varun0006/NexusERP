from app.extensions import db
from datetime import datetime


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    codename = db.Column(db.String(80), unique=True, nullable=False)
    module = db.Column(db.String(80))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Permission {self.codename}>"
