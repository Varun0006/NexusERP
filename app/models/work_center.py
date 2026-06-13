from app.extensions import db
from datetime import datetime


class WorkCenter(db.Model):
    __tablename__ = "work_centers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    department = db.Column(db.String(80))
    capacity_per_shift = db.Column(db.Float, default=1.0)
    cost_per_hour = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_orders = db.relationship("WorkOrder", backref="work_center", lazy="dynamic")
    bom_operations = db.relationship("BomOperation", backref="work_center", lazy="dynamic")

    def __repr__(self):
        return f"<WorkCenter {self.name}>"
