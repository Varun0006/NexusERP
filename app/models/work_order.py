from app.extensions import db
from datetime import datetime


class WorkOrder(db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)
    mo_id = db.Column(db.Integer, db.ForeignKey("manufacturing_orders.id"), nullable=False)
    work_center_id = db.Column(db.Integer, db.ForeignKey("work_centers.id"), nullable=False)
    operation_name = db.Column(db.String(200))
    sequence = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="pending")
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Float, default=0.0)
    completion_percent = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_user = db.relationship("User", backref="work_orders")

    def __repr__(self):
        return f"<WorkOrder {self.operation_name}>"
