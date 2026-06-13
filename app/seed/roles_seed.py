from app.extensions import db
from app.models.role import Role
from app.models.permission import Permission


def seed_roles_and_permissions():
    permissions_data = [
        ("Manage Users", "manage_users", "auth"),
        ("View Products", "view_products", "products"),
        ("Create Products", "create_products", "products"),
        ("Edit Products", "edit_products", "products"),
        ("Delete Products", "delete_products", "products"),
        ("View Inventory", "view_inventory", "inventory"),
        ("Adjust Inventory", "adjust_inventory", "inventory"),
        ("View Sales", "view_sales", "sales"),
        ("Create Sales", "create_sales", "sales"),
        ("Confirm Sales", "confirm_sales", "sales"),
        ("Deliver Sales", "deliver_sales", "sales"),
        ("View Purchases", "view_purchases", "purchase"),
        ("Create Purchases", "create_purchases", "purchase"),
        ("Confirm Purchases", "confirm_purchases", "purchase"),
        ("Receive Purchases", "receive_purchases", "purchase"),
        ("View BOM", "view_bom", "bom"),
        ("Create BOM", "create_bom", "bom"),
        ("View Manufacturing", "view_manufacturing", "manufacturing"),
        ("Create Manufacturing", "create_manufacturing", "manufacturing"),
        ("View Reports", "view_reports", "reports"),
        ("View Audit Logs", "view_audit", "audit"),
        ("Run Procurement", "run_procurement", "procurement"),
    ]
    for name, codename, module in permissions_data:
        if not Permission.query.filter_by(codename=codename).first():
            db.session.add(Permission(name=name, codename=codename, module=module))
    db.session.flush()
    roles_data = {
        "Admin": {"description": "Full system access"},
        "Manager": {"description": "Can manage operations"},
        "Staff": {"description": "Can view and create"},
    }
    for role_name, info in roles_data.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=info["description"])
            db.session.add(role)
            db.session.flush()
        if role_name == "Admin":
            all_perms = Permission.query.all()
            role.permissions = all_perms
        elif role_name == "Manager":
            for p in Permission.query.filter(
                ~Permission.codename.in_(["manage_users", "delete_products", "view_audit"])
            ).all():
                if p not in role.permissions:
                    role.permissions.append(p)
    db.session.commit()
