from app.models.sales_order_line import SalesOrderLine
from app.models.sales_order import SalesOrder
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta


class DemandForecast:
    def forecast_product(self, product_id, days_ahead=30):
        data = (
            db.session.query(
                func.date(SalesOrder.order_date).label("date"),
                func.sum(SalesOrderLine.quantity).label("qty"),
            )
            .join(SalesOrderLine, SalesOrder.id == SalesOrderLine.sales_order_id)
            .filter(
                SalesOrderLine.product_id == product_id,
                SalesOrder.order_date >= datetime.utcnow() - timedelta(days=90),
            )
            .group_by(func.date(SalesOrder.order_date))
            .order_by(func.date(SalesOrder.order_date))
            .all()
        )
        if not data:
            return {"product_id": product_id, "forecast": 0, "confidence": "low"}
        total_qty = sum(d.qty for d in data)
        avg_daily = total_qty / len(data) if data else 0
        return {
            "product_id": product_id,
            "forecast": round(avg_daily * days_ahead, 0),
            "avg_daily": round(avg_daily, 2),
            "confidence": "medium" if len(data) > 30 else "low",
        }

    def forecast_all(self, days_ahead=30):
        product_ids = [r[0] for r in db.session.query(SalesOrderLine.product_id).distinct().all()]
        return [self.forecast_product(pid, days_ahead) for pid in product_ids]
