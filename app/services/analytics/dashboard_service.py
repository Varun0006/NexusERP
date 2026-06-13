from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.manufacturing_order import ManufacturingOrder
from sqlalchemy import func
from datetime import datetime, timedelta


class DashboardService:
    def get_kpi_summary(self):
        total_revenue = (
            db.session.query(func.sum(SalesOrder.total_amount))
            .filter(SalesOrder.status.in_(["delivered", "closed"]))
            .scalar()
            or 0
        )
        total_cost = (
            db.session.query(func.sum(PurchaseOrder.total_amount))
            .filter(PurchaseOrder.status.in_(["received", "closed"]))
            .scalar()
            or 0
        )
        return {
            "revenue": total_revenue,
            "costs": total_cost,
            "profit": total_revenue - total_cost,
            "product_count": Product.query.count(),
            "low_stock": Inventory.query.filter(
                Inventory.on_hand_qty <= Product.safety_stock
            ).count(),
            "pending_mos": ManufacturingOrder.query.filter(
                ~ManufacturingOrder.status.in_(["completed", "cancelled"])
            ).count(),
        }

    def get_sales_trend(self, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        return (
            db.session.query(
                func.date(SalesOrder.order_date).label("date"),
                func.sum(SalesOrder.total_amount).label("total"),
            )
            .filter(SalesOrder.order_date >= since)
            .group_by(func.date(SalesOrder.order_date))
            .order_by(func.date(SalesOrder.order_date))
            .all()
        )
