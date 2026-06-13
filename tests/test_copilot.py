from datetime import datetime, timedelta


def _login_copilot_user(client, db):
    from app.models.role import Role
    from app.models.user import User

    role = Role.query.filter_by(name="Business Owner").first() or Role.query.first()
    user = User(username="copilot_user", email="copilot_user@test.com", role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"username": "copilot_user", "password": "pass123"})


def test_copilot_page_loads(client, db):
    _login_copilot_user(client, db)

    response = client.get("/copilot/")

    assert response.status_code == 200
    assert b"AI Operations Copilot" in response.data


def test_copilot_chat_low_stock_response(client, db):
    from app.models.category import Category
    from app.models.inventory import Inventory
    from app.models.product import Product

    _login_copilot_user(client, db)

    category = Category(name="Copilot Category")
    db.session.add(category)
    db.session.flush()

    product = Product(
        name="Critical Screw",
        sku="RAW-COP-001",
        category_id=category.id,
        safety_stock=20,
        procurement_type="mts",
        product_type="raw_material",
        is_active=True,
    )
    db.session.add(product)
    db.session.flush()

    inventory = Inventory(product_id=product.id, on_hand_qty=4, reserved_qty=0)
    db.session.add(inventory)
    db.session.commit()

    response = client.post("/copilot/api/chat", json={"message": "Which products are running low?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["intent"] == "low_stock"
    assert "Critical Screw" in payload["response"]


def test_copilot_delayed_order_analysis(client, db):
    from app.models.category import Category
    from app.models.customer import Customer
    from app.models.inventory import Inventory
    from app.models.product import Product
    from app.models.sales_order import SalesOrder
    from app.models.sales_order_line import SalesOrderLine

    _login_copilot_user(client, db)

    customer = Customer(name="Delay Customer", email="delay@test.com")
    category = Category(name="Delay Category")
    db.session.add(customer)
    db.session.add(category)
    db.session.flush()

    product = Product(
        name="Delayed Cabinet",
        sku="FG-DEL-001",
        category_id=category.id,
        procurement_type="mts",
        product_type="finished_goods",
        is_active=True,
    )
    db.session.add(product)
    db.session.flush()

    inventory = Inventory(product_id=product.id, on_hand_qty=1, reserved_qty=0)
    db.session.add(inventory)

    order = SalesOrder(
        order_number="SO-DELAY-001",
        customer_id=customer.id,
        status="confirmed",
        expected_date=datetime.utcnow() - timedelta(days=2),
    )
    db.session.add(order)
    db.session.flush()

    line = SalesOrderLine(
        sales_order_id=order.id,
        product_id=product.id,
        quantity=8,
        delivered_qty=0,
        unit_price=100,
        line_total=800,
    )
    db.session.add(line)
    db.session.commit()

    response = client.post("/copilot/api/chat", json={"message": "Why is SO-DELAY-001 delayed?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["intent"] == "delayed_order"
    assert "Delay analysis for SO-DELAY-001" in payload["response"]
    assert "Stock shortage" in payload["response"]


def test_copilot_context_endpoint(client, db):
    _login_copilot_user(client, db)

    response = client.get("/copilot/api/context")

    assert response.status_code == 200
    payload = response.get_json()
    assert "open_sales_orders" in payload
    assert "active_manufacturing_orders" in payload
