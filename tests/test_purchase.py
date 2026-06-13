def test_purchase_page(client, db):
    from app.models.user import User
    user = User(username="po_test", email="po@test.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "po_test", "password": "test"})
    response = client.get("/purchase/")
    assert response.status_code == 200
