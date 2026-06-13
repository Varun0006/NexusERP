from app.extensions import db
from datetime import datetime


class Bom(db.Model):
    __tablename__ = "boms"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(20), default="1.0")
    quantity = db.Column(db.Float, default=1.0)
    is_active = db.Column(db.Boolean, default=True)
    total_cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    components = db.relationship("BomComponent", backref="bom", lazy="dynamic", cascade="all, delete-orphan")
    operations = db.relationship("BomOperation", backref="bom", lazy="dynamic", cascade="all, delete-orphan")

    def calculate_cost(self):
        material_cost = sum(c.total_cost for c in self.components.all())
        operation_cost = sum(o.cost for o in self.operations.all())
        self.total_cost = material_cost + operation_cost
        return self.total_cost

    def __repr__(self):
        return f"<Bom {self.name} v{self.version}>"
