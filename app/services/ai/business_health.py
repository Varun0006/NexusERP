from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.product import Product
from app.extensions import db
from sqlalchemy import func


class BusinessHealth:
    def calculate_health_score(self):
        score = 100
        reasons = []
        # Revenue check
        total_revenue = (
            db.session.query(func.sum(SalesOrder.total_amount))
            .filter(SalesOrder.status.in_(["delivered", "closed"]))
            .scalar()
            or 0
        )
        if total_revenue == 0:
            score -= 20
            reasons.append("No revenue recorded")
        # Inventory health
        low_stock = Inventory.query.filter(
            Inventory.on_hand_qty <= Product.safety_stock
        ).count()
        if low_stock > 5:
            score -= 10
            reasons.append(f"{low_stock} products below safety stock")
        # Stockout risk
        zero_stock = Inventory.query.filter(Inventory.on_hand_qty == 0).count()
        if zero_stock > 0:
            score -= 15
            reasons.append(f"{zero_stock} products out of stock")
        return {
            "score": max(score, 0),
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor",
            "reasons": reasons,
            "total_revenue": total_revenue,
        }
