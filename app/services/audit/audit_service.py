from app.extensions import db
from app.models.audit_log import AuditLog
from datetime import datetime


class AuditService:
    def log(
        self,
        user_id,
        action,
        module,
        reference_type=None,
        reference_id=None,
        reference_number=None,
        description=None,
        ip_address=None,
        old_values=None,
        new_values=None,
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            description=description,
            ip_address=ip_address,
            old_values=str(old_values) if old_values else None,
            new_values=str(new_values) if new_values else None,
        )
        db.session.add(log)
        db.session.commit()
        return log

    def get_logs(self, module=None, limit=50):
        query = AuditLog.query
        if module:
            query = query.filter_by(module=module)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    def get_module_logs(self, module, reference_id):
        return (
            AuditLog.query.filter_by(module=module, reference_id=reference_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )
