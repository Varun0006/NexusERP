from app.extensions import db
from app.models.stock_ledger import StockLedger


class LedgerService:
    @staticmethod
    def record_movement(product_id, movement_type, quantity, before_qty, after_qty,
                        reference_type=None, reference_id=None, reference_number=None,
                        unit_price=0.0, notes=None, user_id=None):
        entry = StockLedger(
            product_id=product_id,
            movement_type=movement_type,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            quantity=quantity,
            before_qty=before_qty,
            after_qty=after_qty,
            unit_price=unit_price,
            total_value=quantity * unit_price,
            notes=notes,
            user_id=user_id,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_movements_for_product(product_id, limit=100):
        return StockLedger.query.filter_by(product_id=product_id)\
            .order_by(StockLedger.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all_movements(limit=200):
        return StockLedger.query.order_by(StockLedger.created_at.desc()).limit(limit).all()
