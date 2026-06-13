from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.sales_order_line import SalesOrderLine
from app.models.product import Product
from app.models.inventory import Inventory
from sqlalchemy import func
from datetime import datetime, timedelta


class ReportService:
    def generate_sales_report(self, start_date, end_date):
        return (
            db.session.query(
                func.date(SalesOrder.order_date).label("date"),
                func.count(SalesOrder.id).label("order_count"),
                func.sum(SalesOrder.total_amount).label("revenue"),
            )
            .filter(
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
            )
            .group_by(func.date(SalesOrder.order_date))
            .order_by(func.date(SalesOrder.order_date))
            .all()
        )

    def top_selling_products(self, limit=10):
        return (
            db.session.query(
                Product.name,
                Product.sku,
                func.sum(SalesOrderLine.quantity).label("total_qty"),
                func.sum(SalesOrderLine.line_total).label("total_revenue"),
            )
            .join(SalesOrderLine, Product.id == SalesOrderLine.product_id)
            .group_by(Product.id)
            .order_by(func.sum(SalesOrderLine.line_total).desc())
            .limit(limit)
            .all()
        )

    def inventory_valuation(self):
        items = (
            db.session.query(
                Product.name,
                Product.sku,
                Inventory.on_hand_qty,
                Product.cost_price,
                (Inventory.on_hand_qty * Product.cost_price).label("value"),
            )
            .join(Inventory, Product.id == Inventory.product_id)
            .all()
        )
        total_value = sum(item.value for item in items)
        return items, total_value
