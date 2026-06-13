def _create_user_with_role(db, username, email, role_name):
    from app.models.role import Role
    from app.models.user import User

    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=email, role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)
    db.session.commit()
    return user


def test_auto_audit_log_created_for_sales_order(client, db):
    from app.models.audit_log import AuditLog
    from app.models.category import Category
    from app.models.customer import Customer
    from app.models.product import Product

    user = _create_user_with_role(db, "audit_sales", "audit_sales@test.com", "Sales User")

    customer = Customer(name="Audit Customer", email="audit_customer@test.com")
    category = Category(name="Audit Category")
    db.session.add(customer)
    db.session.add(category)
    db.session.flush()

    product = Product(
        name="Audit Product",
        sku="FG-AUD-001",
        category_id=category.id,
        sales_price=1500.0,
        product_type="finished_goods",
        procurement_type="mts",
        is_active=True,
    )
    db.session.add(product)
    db.session.commit()

    client.post("/auth/login", data={"username": user.username, "password": "pass123"})

    response = client.post(
        "/sales/create",
        data={"customer_id": customer.id, "notes": "Created from audit test"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    log = (
        AuditLog.query.filter_by(module="sales_orders", action="create")
        .order_by(AuditLog.created_at.desc())
        .first()
    )
    assert log is not None
    assert log.user_id == user.id



def test_audit_logs_page_with_filters(client, db):
    from app.services.audit.audit_service import AuditService

    owner = _create_user_with_role(db, "audit_owner", "audit_owner@test.com", "Business Owner")

    audit_service = AuditService()
    audit_service.log(
        user_id=owner.id,
        action="update",
        module="products",
        reference_type="products",
        reference_id=101,
        reference_number="FG-001",
        description="Updated product cost",
        old_values={"cost_price": 90},
        new_values={"cost_price": 100},
    )

    client.post("/auth/login", data={"username": owner.username, "password": "pass123"})

    response = client.get("/audit/?module=products&action=update&q=FG-001")

    assert response.status_code == 200
    assert b"Audit Logs" in response.data
    assert b"Updated product cost" in response.data
