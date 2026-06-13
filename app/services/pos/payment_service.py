from app.extensions import db
from app.models.pos_order import PosOrder


class PaymentService:
    PAYMENT_METHODS = ["cash", "card", "upi", "credit"]

    def process_payment(self, order_id, amount, method="cash"):
        order = PosOrder.query.get(order_id)
        if not order:
            return None
        if method not in self.PAYMENT_METHODS:
            method = "cash"
        order.payment_method = method
        order.payment_status = "paid"
        db.session.commit()
        return order

    def refund_order(self, order_id):
        order = PosOrder.query.get(order_id)
        if order:
            order.payment_status = "refunded"
            db.session.commit()
        return order
