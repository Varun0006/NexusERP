from app.extensions import db
from datetime import datetime


class PosSession(db.Model):
    __tablename__ = "pos_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_number = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    opening_balance = db.Column(db.Float, default=0.0)
    closing_balance = db.Column(db.Float, default=0.0)
    total_sales = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="open")
    notes = db.Column(db.Text)

    cashier = db.relationship("User", backref="pos_sessions")
    orders = db.relationship("PosOrder", backref="session", lazy="dynamic")

    def __repr__(self):
        return f"<PosSession {self.session_number}>"
