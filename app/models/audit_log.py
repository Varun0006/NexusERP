from app.extensions import db
from datetime import datetime


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(80), nullable=False)
    module = db.Column(db.String(80), nullable=False)
    reference_type = db.Column(db.String(80))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(80))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.module}>"
