from app.extensions import db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.procurement_request import ProcurementRequest


class ReorderEngine:
    def check_reorder(self):
        triggered = []
        products = Product.query.filter(
            Product.procurement_type == "mts", Product.reorder_level > 0
        ).all()
        for product in products:
            inv = Inventory.query.filter_by(product_id=product.id).first()
            if inv and inv.on_hand_qty <= product.reorder_level:
                qty = product.reorder_level * 2
                triggered.append(
                    {
                        "product": product,
                        "quantity": qty,
                        "current_stock": inv.on_hand_qty,
                    }
                )
        return triggered
