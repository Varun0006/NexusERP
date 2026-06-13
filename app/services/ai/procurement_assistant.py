import json
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_line import SalesOrderLine
from app.models.procurement_rule import ProcurementRule
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta


class ProcurementAssistant:
    def analyze_inventory_health(self):
        low_stock = []
        overstock = []
        products = Product.query.filter_by(is_active=True).all()
        for product in products:
            inv = Inventory.query.filter_by(product_id=product.id).first()
            if not inv:
                continue
            if inv.on_hand_qty <= product.safety_stock:
                low_stock.append(
                    {
                        "product": product.name,
                        "sku": product.sku,
                        "on_hand": inv.on_hand_qty,
                        "safety_stock": product.safety_stock,
                    }
                )
            elif inv.on_hand_qty > product.reorder_level * 3:
                overstock.append(
                    {
                        "product": product.name,
                        "sku": product.sku,
                        "on_hand": inv.on_hand_qty,
                    }
                )
        return {"low_stock": low_stock, "overstock": overstock, "total_products": len(products)}

    def suggest_reorder(self, product_id):
        product = Product.query.get(product_id)
        inv = Inventory.query.filter_by(product_id=product_id).first()
        if not inv:
            return {"suggest": "setup_inventory"}
        daily_sales = (
            db.session.query(func.sum(SalesOrderLine.quantity))
            .join(SalesOrderLine.order)
            .filter(
                SalesOrderLine.product_id == product_id,
                SalesOrder.order_date >= datetime.utcnow() - timedelta(days=30),
            )
            .scalar()
            or 0
        )
        avg_daily = daily_sales / 30
        days_until_stockout = inv.on_hand_qty / avg_daily if avg_daily > 0 else 999
        return {
            "product": product.name,
            "current_stock": inv.on_hand_qty,
            "avg_daily_sales": round(avg_daily, 2),
            "days_until_stockout": round(days_until_stockout, 1),
            "suggested_order_qty": max(
                round(avg_daily * product.lead_time_days * 1.5 - inv.on_hand_qty, 0), 0
            ),
        }
