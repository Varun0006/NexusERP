from app.extensions import db
from datetime import datetime


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(80), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="draft")
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lines = db.relationship("PurchaseOrderLine", backref="order", lazy="dynamic", cascade="all, delete-orphan")
    created_by = db.relationship("User", backref="purchase_orders")

    @property
    def is_received(self):
        return self.status in ("received", "closed")

    def __repr__(self):
        return f"<PurchaseOrder {self.order_number}>"
