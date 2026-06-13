from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.sales_order_line import SalesOrderLine
from app.services.inventory.stock_service import StockService
from app.services.inventory.ledger_service import LedgerService
from datetime import datetime


class DeliveryService:
    @staticmethod
    def deliver_order(order_id, user_id=None):
        order = SalesOrder.query.get(order_id)
        if not order:
            return None, "Order not found"
        if order.status not in ("confirmed", "partially_delivered"):
            return None, "Order cannot be delivered"

        all_delivered = True
        for line in order.lines.all():
            remaining = line.quantity - line.delivered_qty
            if remaining > 0:
                success, inv = StockService.consume_stock(line.product_id, remaining, user_id)
                if not success:
                    return None, f"Failed to consume stock for {line.product.name}"
                line.delivered_qty = line.quantity
                LedgerService.record_movement(
                    product_id=line.product_id,
                    movement_type="sales_delivery",
                    quantity=-remaining,
                    before_qty=inv.on_hand_qty + remaining if inv else 0,
                    after_qty=inv.on_hand_qty if inv else 0,
                    reference_type="sales_order",
                    reference_id=order.id,
                    reference_number=order.order_number,
                    user_id=user_id,
                )

        order.status = "delivered" if all_delivered else "partially_delivered"
        order.delivery_date = datetime.utcnow()
        db.session.commit()
        return order, None
