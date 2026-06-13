from app.extensions import db
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_ledger import StockLedger


class InventoryService:
    @staticmethod
    def get_or_create_inventory(product_id):
        inv = Inventory.query.filter_by(product_id=product_id).first()
        if not inv:
            inv = Inventory(product_id=product_id)
            db.session.add(inv)
            db.session.commit()
        return inv

    @staticmethod
    def adjust_stock(product_id, quantity, reason, user_id=None):
        inv = InventoryService.get_or_create_inventory(product_id)
        before = inv.on_hand_qty
        inv.on_hand_qty += quantity
        if inv.on_hand_qty < 0:
            return False, "Stock cannot be negative"
        db.session.flush()

        entry = StockLedger(
            product_id=product_id,
            movement_type="adjustment",
            reference_type="adjustment",
            quantity=quantity,
            before_qty=before,
            after_qty=inv.on_hand_qty,
            notes=reason,
            user_id=user_id,
        )
        db.session.add(entry)
        db.session.commit()
        return True, inv

    @staticmethod
    def get_low_stock_products():
        return Inventory.query.filter(
            Inventory.on_hand_qty <= Inventory.product.has(Product.is_active.is_(True))
        ).all()

    @staticmethod
    def get_stock_value():
        inventories = Inventory.query.all()
        return sum(inv.on_hand_qty * inv.product.cost_price for inv in inventories if inv.product)
