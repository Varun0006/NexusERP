import json
from datetime import datetime

from flask import has_request_context, request
from flask_login import current_user
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


_HOOKS_REGISTERED = False
_EXCLUDED_FIELDS = {"password_hash", "created_at", "updated_at", "last_login"}


def _is_auditable(obj):
    return hasattr(obj, "__table__") and not isinstance(obj, AuditLog)


def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)


def _snapshot_object(obj):
    mapper = inspect(obj).mapper
    snapshot = {}
    for attr in mapper.column_attrs:
        key = attr.key
        if key in _EXCLUDED_FIELDS:
            continue
        snapshot[key] = _serialize_value(getattr(obj, key))
    return snapshot


def _changed_values(obj):
    state = inspect(obj)
    mapper = state.mapper
    old_values = {}
    new_values = {}

    for attr in mapper.column_attrs:
        key = attr.key
        if key in _EXCLUDED_FIELDS:
            continue

        history = state.attrs[key].history
        if not history.has_changes():
            continue

        old_val = history.deleted[0] if history.deleted else None
        new_val = history.added[0] if history.added else getattr(obj, key)
        old_values[key] = _serialize_value(old_val)
        new_values[key] = _serialize_value(new_val)

    return old_values, new_values


def _module_for(obj):
    return getattr(obj, "__tablename__", obj.__class__.__name__.lower())


def _reference_number_for(obj):
    fields = ["order_number", "mo_number", "request_number", "sku", "username", "name"]
    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value:
                return str(value)
    return None


def _current_user_id():
    if not has_request_context():
        return None
    try:
        return current_user.id if current_user.is_authenticated else None
    except Exception:
        return None


def _current_ip_address():
    if not has_request_context():
        return None
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def _description(action, module, reference_number):
    reference = f" ({reference_number})" if reference_number else ""
    if action == "create":
        return f"Created {module}{reference}."
    if action == "update":
        return f"Updated {module}{reference}."
    return f"Deleted {module}{reference}."


def _before_flush(session, flush_context, instances):
    entries = session.info.setdefault("audit_entries", [])

    for obj in session.new:
        if not _is_auditable(obj):
            continue
        entries.append({"obj": obj, "action": "create", "old": None, "new": _snapshot_object(obj)})

    for obj in session.deleted:
        if not _is_auditable(obj):
            continue
        entries.append({"obj": obj, "action": "delete", "old": _snapshot_object(obj), "new": None})

    for obj in session.dirty:
        if not _is_auditable(obj):
            continue
        if not session.is_modified(obj, include_collections=False):
            continue
        old_values, new_values = _changed_values(obj)
        if not old_values and not new_values:
            continue
        entries.append({"obj": obj, "action": "update", "old": old_values, "new": new_values})


def _after_flush(session, flush_context):
    entries = session.info.pop("audit_entries", [])
    if not entries:
        return

    user_id = _current_user_id()
    ip_address = _current_ip_address()

    for entry in entries:
        obj = entry["obj"]
        if not _is_auditable(obj):
            continue

        module = _module_for(obj)
        reference_number = _reference_number_for(obj)
        reference_id = getattr(obj, "id", None)
        action = entry["action"]

        log = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            reference_type=module,
            reference_id=reference_id,
            reference_number=reference_number,
            description=_description(action, module, reference_number),
            ip_address=ip_address,
            old_values=json.dumps(entry["old"], default=str) if entry["old"] else None,
            new_values=json.dumps(entry["new"], default=str) if entry["new"] else None,
        )
        session.add(log)


def register_audit_hooks():
    global _HOOKS_REGISTERED
    if _HOOKS_REGISTERED:
        return

    event.listen(Session, "before_flush", _before_flush)
    event.listen(Session, "after_flush", _after_flush)
    _HOOKS_REGISTERED = True