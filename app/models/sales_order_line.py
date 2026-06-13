from app.extensions import db


class SalesOrderLine(db.Model):
    __tablename__ = "sales_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey("sales_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)
    tax_percent = db.Column(db.Float, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    delivered_qty = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<SalesOrderLine {self.product_id} qty={self.quantity}>"
