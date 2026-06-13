from app.extensions import db
from app.models.procurement_rule import ProcurementRule
from app.models.procurement_request import ProcurementRequest
from app.models.inventory import Inventory
from app.models.product import Product
from datetime import datetime


class ProcurementEngine:
    def run(self):
        requests_created = 0
        rules = ProcurementRule.query.filter_by(is_active=True).all()
        for rule in rules:
            inv = Inventory.query.filter_by(product_id=rule.product_id).first()
            on_hand = inv.on_hand_qty if inv else 0
            reserved = inv.reserved_qty if inv else 0
            available = on_hand - reserved
            product = Product.query.get(rule.product_id)
            if available < product.reorder_level:
                qty = product.reorder_level - available
                if qty >= rule.min_order_qty:
                    req = ProcurementRequest(
                        request_number=f"PR-{ProcurementRequest.query.count() + 1:05d}",
                        product_id=rule.product_id,
                        quantity=qty,
                        source_type=rule.source_type,
                        status="open",
                    )
                    db.session.add(req)
                    requests_created += 1
        db.session.commit()
        return requests_created
