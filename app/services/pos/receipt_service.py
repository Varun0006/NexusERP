from app.models.pos_order import PosOrder


class ReceiptService:
    def generate_receipt_data(self, order_id):
        order = PosOrder.query.get(order_id)
        if not order:
            return None
        return {
            "receipt_number": order.receipt_number or order.order_number,
            "order_number": order.order_number,
            "date": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "cashier": order.session.cashier.full_name if order.session.cashier else "",
            "customer": order.customer.name if order.customer else "Walk-in",
            "items": [
                {
                    "name": line.product.name,
                    "qty": line.quantity,
                    "price": line.unit_price,
                    "total": line.line_total,
                }
                for line in order.lines
            ],
            "subtotal": order.subtotal,
            "tax": order.tax_amount,
            "total": order.total_amount,
            "payment_method": order.payment_method,
        }
