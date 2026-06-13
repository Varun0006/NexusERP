from app.extensions import db
from datetime import datetime


class SalesOrder(db.Model):
    __tablename__ = "sales_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(80), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="draft")
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lines = db.relationship("SalesOrderLine", backref="order", lazy="dynamic", cascade="all, delete-orphan")
    created_by = db.relationship("User", backref="sales_orders")

    @property
    def is_delivered(self):
        return self.status in ("delivered", "closed")

    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"
