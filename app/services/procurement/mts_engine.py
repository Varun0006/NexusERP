from app.extensions import db
from app.models.procurement_rule import ProcurementRule
from app.models.inventory import Inventory
from app.models.procurement_request import ProcurementRequest


class MtsEngine:
    def evaluate(self):
        requests = []
        rules = ProcurementRule.query.filter_by(
            procurement_type="mts", is_active=True
        ).all()
        for rule in rules:
            inv = Inventory.query.filter_by(product_id=rule.product_id).first()
            if inv and inv.free_to_use_qty <= inv.product.reorder_level:
                qty = inv.product.reorder_level - inv.free_to_use_qty
                if qty >= rule.min_order_qty:
                    requests.append(
                        {
                            "product": rule.product,
                            "quantity": qty,
                            "source_type": rule.source_type,
                            "vendor": rule.vendor,
                        }
                    )
        return requests
