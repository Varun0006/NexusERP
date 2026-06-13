def test_sales_page(client, db):
    from app.models.user import User
    user = User(username="sales_test", email="sales@test.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "sales_test", "password": "test"})
    response = client.get("/sales/")
    assert response.status_code == 200
