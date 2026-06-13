from app.extensions import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    barcode = db.Column(db.String(80), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, default=0.0)
    sales_price = db.Column(db.Float, default=0.0)
    tax_percent = db.Column(db.Float, default=0.0)
    product_type = db.Column(db.String(20), default="finished_goods")
    unit_of_measure = db.Column(db.String(20), default="pcs")
    is_active = db.Column(db.Boolean, default=True)
    reorder_level = db.Column(db.Float, default=0.0)
    safety_stock = db.Column(db.Float, default=0.0)
    procurement_type = db.Column(db.String(20), default="mts")
    lead_time_days = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("Category", backref="products")
    inventory = db.relationship("Inventory", backref="product", uselist=False)
    bom = db.relationship("Bom", backref="product", uselist=False)
    sale_lines = db.relationship("SalesOrderLine", backref="product", lazy="dynamic")
    purchase_lines = db.relationship("PurchaseOrderLine", backref="product", lazy="dynamic")

    def __repr__(self):
        return f"<Product {self.name} ({self.sku})>"
