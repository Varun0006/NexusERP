from app.extensions import db
from datetime import datetime


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    pincode = db.Column(db.String(20))
    gst_number = db.Column(db.String(30))
    payment_terms = db.Column(db.String(200))
    lead_time_days = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    purchase_orders = db.relationship("PurchaseOrder", backref="vendor", lazy="dynamic")

    def __repr__(self):
        return f"<Vendor {self.name}>"
