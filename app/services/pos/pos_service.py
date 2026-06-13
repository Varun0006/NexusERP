from app.extensions import db
from app.models.pos_session import PosSession
from app.models.pos_order import PosOrder
from app.models.pos_order_line import PosOrderLine
from app.models.product import Product
from datetime import datetime


class PosService:
    def open_session(self, user_id, opening_balance=0.0):
        session = PosSession(
            session_number=f"POS-{PosSession.query.count() + 1:05d}",
            user_id=user_id,
            opening_balance=opening_balance,
        )
        db.session.add(session)
        db.session.commit()
        return session

    def close_session(self, session_id, closing_balance=0.0):
        session = PosSession.query.get(session_id)
        if session:
            session.status = "closed"
            session.closed_at = datetime.utcnow()
            session.closing_balance = closing_balance
            db.session.commit()
        return session

    def create_order(self, session_id, items, customer_id=None, payment_method="cash"):
        session = PosSession.query.get(session_id)
        order = PosOrder(
            order_number=f"POS-ORD-{PosOrder.query.count() + 1:05d}",
            session_id=session_id,
            customer_id=customer_id,
            payment_method=payment_method,
        )
        db.session.add(order)
        db.session.flush()
        subtotal = 0
        tax_total = 0
        for item in items:
            product = Product.query.get(item["product_id"])
            line_total = item["quantity"] * item.get("unit_price", product.sales_price)
            line_tax = line_total * item.get("tax_percent", product.tax_percent) / 100
            line = PosOrderLine(
                pos_order_id=order.id,
                product_id=product.id,
                quantity=item["quantity"],
                unit_price=item.get("unit_price", product.sales_price),
                tax_percent=item.get("tax_percent", product.tax_percent),
                line_total=line_total,
            )
            db.session.add(line)
            subtotal += line_total
            tax_total += line_tax
            inv = product.inventory
            if inv:
                inv.on_hand_qty -= item["quantity"]
        order.subtotal = subtotal
        order.tax_amount = tax_total
        order.total_amount = subtotal + tax_total
        session.total_sales += order.total_amount
        db.session.commit()
        return order
