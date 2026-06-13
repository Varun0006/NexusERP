from app.extensions import db
from datetime import datetime


class PosOrder(db.Model):
    __tablename__ = "pos_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(80), unique=True, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("pos_sessions.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20), default="cash")
    payment_status = db.Column(db.String(20), default="paid")
    receipt_number = db.Column(db.String(80))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer", backref="pos_orders")
    lines = db.relationship("PosOrderLine", backref="order", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PosOrder {self.order_number}>"
