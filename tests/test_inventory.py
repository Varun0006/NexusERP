def test_stock_view(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role.query.filter_by(name="Inventory Manager").first()
    user = User(username="test", email="test@test.com", role_id=role.id)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "test", "password": "test"})
    response = client.get("/inventory/")
    assert response.status_code == 200


def test_product_creation_and_details(client, db):
    from app.models.user import User
    from app.models.role import Role
    from app.models.category import Category
    from app.models.product import Product
    from app.models.inventory import Inventory
    
    # Setup inventory manager user
    role = Role.query.filter_by(name="Inventory Manager").first()
    user = User(username="inv_mgr", email="inv_mgr@test.com", role_id=role.id)
    user.set_password("mgrpass")
    db.session.add(user)
    
    # Create category for form choices
    cat = Category(name="Test Materials")
    db.session.add(cat)
    db.session.commit()
    
    client.post("/auth/login", data={"username": "inv_mgr", "password": "mgrpass"})
    
    # Create product via form POST
    response = client.post("/products/create", data={
        "name": "New Brass Bolt",
        "sku": "RAW-BRS-001",
        "barcode": "987654321",
        "category_id": cat.id,
        "product_type": "raw_material",
        "unit_of_measure": "pcs",
        "description": "Premium brass bolt",
        "cost_price": 50.0,
        "sales_price": 85.0,
        "tax_percent": 18.0,
        "reorder_level": 100,
        "safety_stock": 25,
        "procurement_type": "mts",
        "lead_time_days": 3,
        "is_active": True
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify product was created and associated inventory record was initialized
    prod = Product.query.filter_by(sku="RAW-BRS-001").first()
    assert prod is not None
    assert prod.inventory is not None
    assert prod.inventory.on_hand_qty == 0.0
    assert prod.inventory.reserved_qty == 0.0
    
    # Verify details page loads successfully
    response = client.get(f"/products/{prod.id}")
    assert response.status_code == 200
    assert b"New Brass Bolt" in response.data
    assert b"RAW-BRS-001" in response.data
    assert b"Free To Use" in response.data
