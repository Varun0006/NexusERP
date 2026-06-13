from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.stock_ledger import StockLedger
from sqlalchemy import func
from datetime import datetime, timedelta


class KpiService:
    def get_revenue_growth(self):
        now = datetime.utcnow()
        this_month = (
            db.session.query(func.sum(SalesOrder.total_amount))
            .filter(
                SalesOrder.status.in_(["delivered", "closed"]),
                func.strftime("%Y-%m", SalesOrder.order_date)
                == func.strftime("%Y-%m", now),
            )
            .scalar()
            or 0
        )
        return float(this_month)

    def inventory_turnover_ratio(self):
        cog = (
            db.session.query(func.sum(PurchaseOrder.total_amount))
            .filter(PurchaseOrder.status.in_(["received", "closed"]))
            .scalar()
            or 0
        )
        avg_inventory = (
            db.session.query(func.avg(Inventory.on_hand_qty * Product.cost_price))
            .select_from(Inventory)
            .join(Product)
            .scalar()
            or 1
        )
        return float(cog / avg_inventory) if avg_inventory else 0
