from app.extensions import db
from app.models.manufacturing_order import ManufacturingOrder
from app.models.product import Product
from app.models.bom import Bom
from app.models.work_order import WorkOrder
from datetime import datetime


class ManufacturingService:
    def create_mo(self, product_id, quantity, bom_id=None, notes=""):
        product = Product.query.get(product_id)
        if not bom_id:
            bom = Bom.query.filter_by(product_id=product_id, is_active=True).first()
            bom_id = bom.id if bom else None
        mo = ManufacturingOrder(
            mo_number=f"MO-{ManufacturingOrder.query.count() + 1:05d}",
            product_id=product_id,
            bom_id=bom_id,
            quantity=quantity,
            notes=notes,
            status="draft",
        )
        db.session.add(mo)
        db.session.commit()
        return mo

    def confirm_mo(self, mo_id):
        mo = ManufacturingOrder.query.get(mo_id)
        if mo and mo.status == "draft":
            mo.status = "confirmed"
            db.session.commit()
        return mo

    def start_mo(self, mo_id):
        mo = ManufacturingOrder.query.get(mo_id)
        if mo and mo.status == "confirmed":
            mo.status = "in_progress"
            mo.start_date = datetime.utcnow()
            if mo.bom:
                for i, operation in enumerate(mo.bom.operations.all()):
                    wo = WorkOrder(
                        mo_id=mo.id,
                        work_center_id=operation.work_center_id,
                        operation_name=operation.name,
                        sequence=operation.sequence,
                        duration_minutes=operation.duration_minutes,
                        status="pending",
                    )
                    db.session.add(wo)
            db.session.commit()
        return mo
