from app.extensions import db
from app.models.work_order import WorkOrder
from datetime import datetime


class WorkOrderService:
    def start_work_order(self, wo_id):
        wo = WorkOrder.query.get(wo_id)
        if wo:
            wo.status = "in_progress"
            wo.start_time = datetime.utcnow()
            db.session.commit()
        return wo

    def complete_work_order(self, wo_id):
        wo = WorkOrder.query.get(wo_id)
        if wo:
            wo.status = "completed"
            wo.end_time = datetime.utcnow()
            wo.completion_percent = 100.0
            db.session.commit()
        return wo

    def update_progress(self, wo_id, percent):
        wo = WorkOrder.query.get(wo_id)
        if wo:
            wo.completion_percent = percent
            if percent >= 100:
                wo.status = "completed"
                wo.end_time = datetime.utcnow()
            db.session.commit()
        return wo
