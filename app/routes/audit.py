import json
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required
from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.decorators import permission_required

audit_bp = Blueprint("audit", __name__, template_folder="../templates/audit")


@audit_bp.route("/")
@login_required
@permission_required("view_audit")
def logs():
    page = request.args.get("page", 1, type=int)
    module = request.args.get("module", "", type=str).strip()
    action = request.args.get("action", "", type=str).strip()
    user_id = request.args.get("user_id", type=int)
    search = request.args.get("q", "", type=str).strip()
    date_from = request.args.get("date_from", "", type=str).strip()
    date_to = request.args.get("date_to", "", type=str).strip()

    query = AuditLog.query
    if module:
        query = query.filter_by(module=module)

    if action:
        query = query.filter_by(action=action)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            AuditLog.description.ilike(like_term)
            | AuditLog.reference_number.ilike(like_term)
            | AuditLog.module.ilike(like_term)
            | AuditLog.action.ilike(like_term)
        )

    if date_from:
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(AuditLog.created_at >= start_date)
        except ValueError:
            pass

    if date_to:
        try:
            end_date = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(AuditLog.created_at < end_date)
        except ValueError:
            pass

    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)

    for log in logs.items:
        log.old_values_pretty = _pretty_values(log.old_values)
        log.new_values_pretty = _pretty_values(log.new_values)

    modules = (
        AuditLog.query.with_entities(AuditLog.module).distinct().order_by(AuditLog.module).all()
    )
    actions = (
        AuditLog.query.with_entities(AuditLog.action).distinct().order_by(AuditLog.action).all()
    )
    users = (
        db.session.query(User.id, User.username)
        .join(AuditLog, AuditLog.user_id == User.id)
        .distinct()
        .order_by(User.username)
        .all()
    )

    filters = {
        "module": module,
        "action": action,
        "user_id": user_id,
        "q": search,
        "date_from": date_from,
        "date_to": date_to,
    }
    return render_template(
        "audit/logs.html",
        logs=logs,
        modules=[m[0] for m in modules if m[0]],
        actions=[a[0] for a in actions if a[0]],
        users=users,
        filters=filters,
    )


def _pretty_values(raw_value):
    if not raw_value:
        return None
    try:
        parsed = json.loads(raw_value)
        return json.dumps(parsed, indent=2, sort_keys=True)
    except (json.JSONDecodeError, TypeError):
        return str(raw_value)
